#!/usr/bin/env python3

"""
Created on 24 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_identity utility is used to create, update and retrieve AWS Cognito identities. Users (with the exception
of superusers) can only access their own identity.

Typically, once a --create has been successfully performed, the user should store their email address and password
using the cognito_credentials utility. With the exception of the create function, the user's credentials must have
previously been entered before using the cognito_credentials utility.

SYNOPSIS
cognito_identity.py  { -f [-e EMAIL_ADDR] | -c | -r | -u  | -d EMAIL_ADDR } [-i INDENT] [-v]

EXAMPLES
./cognito_identity.py -r

DOCUMENT EXAMPLE
{"username": "8", "creation_date": "2021-11-24T12:51:12Z", "email": "bruno.beloff@southcoastscience.com",
"given_name": "bruno", "family_name": "beloff", "is_super": true}

SEE ALSO
scs_analysis/cognito_credentials

RESOURCES
https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-policies.html
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_identity import CmdCognitoIdentity

from scs_core.aws.security.cognito_account_manager import CognitoCreateManager, CognitoUpdateManager, \
    CognitoDeleteManager

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
    gatekeeper = None
    credentials = None
    authentication = None
    finder = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCognitoIdentity()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('cognito_identity', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)

        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        if not cmd.create:
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

        if not cmd.create:
            finder = CognitoFinder(requests, authentication.id_token)
            logger.info(finder)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            report = sorted(finder.find_by_email(cmd.find_email) if cmd.find_email else finder.find_all())

        if cmd.create:
            given_name = StdIO.prompt("Enter given name: ")
            family_name = StdIO.prompt("Enter family name: ")
            email = StdIO.prompt("Enter email address: ")
            password = StdIO.prompt("Enter password: ")

            if not given_name or not given_name:
                logger.error("Given name and family name are required." % email)
                exit(1)

            if not Datum.is_email_address(email):
                logger.error("The email address '%s' is not valid." % email)
                exit(1)

            if not CognitoUserIdentity.is_valid_password(password):
                logger.error("The password '%s' is not valid." % password)
                exit(1)

            identity = CognitoUserIdentity(None, None, email, given_name, family_name, password)

            manager = CognitoCreateManager(requests)
            report = manager.create(identity)

        if cmd.retrieve:
            report = finder.find_self()

        if cmd.update:
            identity = finder.find_self()

            given_name = StdIO.prompt("Enter given name (%s): ", default=identity.given_name)
            family_name = StdIO.prompt("Enter family name (%s): ", default=identity.family_name)
            email = StdIO.prompt("Enter email (%s): ", default=identity.email)
            password = StdIO.prompt("Enter password (RETURN to keep existing): ", default=None)

            if not given_name or not given_name:
                logger.error("Given name and family name are required." % email)
                exit(1)

            if not Datum.is_email_address(email):
                logger.error("The email address '%s' is not valid." % email)
                exit(1)

            if password and not CognitoUserIdentity.is_valid_password(password):
                logger.error("The password '%s' is not valid." % password)
                exit(1)

            report = CognitoUserIdentity(identity.username, None, email, given_name, family_name, password)

            authentication = gatekeeper.login(credentials)                          # renew credentials
            manager = CognitoUpdateManager(requests, authentication.id_token)
            manager.update(report)

        if cmd.delete:
            manager = CognitoDeleteManager(requests, authentication.id_token)
            manager.delete(cmd.delete_email)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
