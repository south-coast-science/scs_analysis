#!/usr/bin/env python3

"""
Created on 22 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_credentials utility is used to manage the AWS Cognito credentials for the user. The credentials are
composed of an email address and a password. The JSON identity document managed by this utility is encrypted.

The password must be specified when the credentials are created and is required when the credentials are accessed.

SYNOPSIS
cognito_credentials.py [-c CREDENTIALS] [{ -s | -t | -d }] [-v]

EXAMPLES
./cognito_credentials.py -s

FILES
~/SCS/aws/cognito_user_credentials.json

DOCUMENT EXAMPLE
{"email": "bruno.beloff@southcoastscience.com", "password": "hello"}

SEE ALSO
scs_analysis/cognito_identity

RESOURCES
https://stackoverflow.com/questions/42568262/how-to-encrypt-text-with-a-password-in-python
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_credentials import CmdCognitoCredentials

from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials

from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

def load_credentials(credentials_name):
    try:
        password = CognitoUserCredentials.password_from_user()
        return CognitoUserCredentials.load(Host, name=credentials_name, encryption_key=password)

    except (KeyError, ValueError):
        logger.error("incorrect password")
        exit(1)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    credentials = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCognitoCredentials()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('cognito_credentials', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.set:
            credentials = CognitoUserCredentials.from_user(cmd.credentials_name)

            if not credentials.ok():
                logger.error("the identity is not valid")
                exit(1)

            credentials.save(Host, encryption_key=credentials.password)

        elif cmd.test:
            manager = CognitoLoginManager(requests)

            credentials = load_credentials(cmd.credentials_name)

            if credentials is None:
                logger.error("no credentials are available")
                exit(1)

            auth = manager.login(credentials)
            logger.info(auth)

            if auth is None:
                logger.error("invalid auth")
                exit(1)

        elif cmd.delete:
            CognitoUserCredentials.delete(Host)

        else:
            credentials = load_credentials(cmd.credentials_name)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if credentials:
            print(JSONify.dumps(credentials))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
