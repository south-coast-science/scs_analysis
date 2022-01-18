#!/usr/bin/env python3

"""
Created on 10 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_organisation_manager utility is used to

SYNOPSIS
aws_organisation_manager.py  { -F | -R ORG_ID | -U ORG_ID [-n NAME] [-u URL] } [-i INDENT] [-v]

EXAMPLES
./aws_organisation_manager.py -R

DOCUMENT EXAMPLE
{"username": "8", "creation-date": "2021-11-24T12:51:12Z", "confirmation-status": "CONFIRMED", "enabled": true,
"email": "bruno.beloff@southcoastscience.com", "given-name": "Bruno", "family-name": "Beloff", "is-super": true}

SEE ALSO
scs_analysis/cognito_credentials
"""

import requests
import sys

from scs_analysis.cmd.cmd_aws_organisation_manager import CmdAWSOrganisationManager

from scs_core.aws.security.cognito_account_manager import CognitoUpdateManager
from scs_core.aws.security.cognito_finder import CognitoFinder
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials, CognitoUserIdentity

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.comms.stdio import StdIO
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    credentials = None
    authentication = None
    finder = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdAWSOrganisationManager()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('aws_organisation_manager', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        gatekeeper = CognitoLoginManager(requests)

        # CognitoUserCredentials...
        if not CognitoUserCredentials.exists(Host):
            logger.error("Cognito credentials not available.")
            exit(1)

        try:
            password = CognitoUserCredentials.password_from_user()
            credentials = CognitoUserCredentials.load(Host, encryption_key=password)
        except (KeyError, ValueError):
            logger.error("incorrect password")
            exit(1)

        try:
            authentication = gatekeeper.login(credentials)

        except HTTPException as ex:
            logger.error(ex.data)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        finder = CognitoFinder(requests, authentication.id_token)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            report = sorted(finder.find_all())

        if cmd.retrieve:
            report = finder.find_self()

        if cmd.update:
            # find...
            identity = finder.find_self()

            # update identity...
            given_name = StdIO.prompt("Enter given name (%s): ", default=identity.given_name)
            family_name = StdIO.prompt("Enter family name (%s): ", default=identity.family_name)
            email = StdIO.prompt("Enter email (%s): ", default=identity.email)
            password = StdIO.prompt("Enter password (RETURN to keep existing): ", default=None)

            if not Datum.is_email_address(email):
                logger.error("The email address '%s' is not valid." % email)
                exit(1)

            if password and not CognitoUserIdentity.is_valid_password(password):
                logger.error("The password '%s' is not valid." % password)
                exit(1)

            identity = CognitoUserIdentity(identity.username, None, None, None,
                                           email, given_name, family_name, password)

            authentication = gatekeeper.login(credentials)                          # renew credentials
            manager = CognitoUpdateManager(requests, authentication.id_token)
            manager.update(identity)

            # confirm updated...
            report = finder.find_self()

            # update credentials...
            if email != credentials.email:
                credentials.email = email

            if password is not None:
                credentials.password = password

            credentials.save(Host, encryption_key=credentials.password)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
