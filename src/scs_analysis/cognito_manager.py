#!/usr/bin/env python3

"""
Created on 24 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_manager utility is used to manage the AWS Cognito credentials for the user. The credentials are
composed of an email address and a password. The JSON identity document managed by this utility is encrypted.

The password must be specified when the credentials are created and is required when the credentials are accessed.

SYNOPSIS
cognito_manager.py [{ -s | -t | -d }] [-v]

EXAMPLES
./cognito_manager.py -s

FILES
~/SCS/aws/cognito_user_credentials.json

DOCUMENT EXAMPLE
{"email": "bruno.beloff@southcoastscience.com", "password": "hello"}

SEE ALSO
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_manager import CmdCognitoManager

from scs_core.aws.security.cognito_finder import CognitoFinder
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials

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
        # resources...

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
        # run...

        if cmd.create:
            given_name = StdIO.prompt("Enter given name: ")
            family_name = StdIO.prompt("Enter family name: ")
            email = StdIO.prompt("Enter email address: ")
            password = StdIO.prompt("Enter password: ")

        if cmd.find:
            finder = CognitoFinder(requests)
            finder.find(authentication.id_token)


    except KeyboardInterrupt:
        print(file=sys.stderr)
