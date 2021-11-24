#!/usr/bin/env python3

"""
Created on 24 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_manager utility is used to create, update and retrieve AWS Cognito identities. Users (with the exception of
superusers) can only access their own identity.

With the exception of the --create function, the user's credentials must have previously been entered using the
cognito_credentials utility.

SYNOPSIS
cognito_manager.py  { -f [-e EMAIL_ADDR] | -r | -c | -u } [-i INDENT] [-v]

EXAMPLES
./cognito_manager.py -s

DOCUMENT EXAMPLE
{"email": "bruno.beloff@southcoastscience.com", "given_name": "bruno", "family_name": "beloff", "is_super": false}

SEE ALSO
scs_analysis/cognito_credentials
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_manager import CmdCognitoManager

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

def load_credentials():
    try:
        return CognitoUserCredentials.load(Host, encryption_key=CognitoUserCredentials.password_from_user())
    except (KeyError, ValueError):
        logger.error("incorrect password")
        exit(1)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    credentials = None
    authentication = None
    finder = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCognitoManager()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('cognito_manager', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        if not cmd.create:
            login_manager = CognitoLoginManager(requests)

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
                authentication = login_manager.login(credentials)

            except HTTPException as ex:
                logger.error(ex.data)
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not cmd.create:
            finder = CognitoFinder(requests, authentication.id_token)
            logger.error(finder)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.create:
            given_name = StdIO.prompt("Enter given name: ")
            family_name = StdIO.prompt("Enter family name: ")
            email = StdIO.prompt("Enter email address: ")
            password = StdIO.prompt("Enter password: ")

            if not Datum.is_email_address(email):
                logger.error("The email address '%s' is not valid." % email)
                exit(1)

            report = CognitoUserIdentity(None, email, given_name, family_name, password)

            # TODO: do the create
            # TODO: is email address in use?

        if cmd.update:
            identity = finder.find_self()

            given_name = StdIO.prompt("Enter given name (%s): " % identity.given_name, default=identity.given_name)
            family_name = StdIO.prompt("Enter family name (%s): " % identity.family_name, default=identity.family_name)
            email = StdIO.prompt("Enter email (%s): " % identity.email, default=identity.email)

            report = CognitoUserIdentity(identity.username, email, given_name, family_name, None)

            # TODO: do the update

        if cmd.find:
            report = sorted(finder.find_by_email(cmd.email) if cmd.email else finder.find_all())

        if cmd.retrieve:
            report = finder.find_self()

        if report:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)
