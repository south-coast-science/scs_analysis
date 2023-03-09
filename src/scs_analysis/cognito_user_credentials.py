#!/usr/bin/env python3

"""
Created on 22 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_user_credentials utility is used to manage the AWS Cognito credentials for the user. The credentials are
composed of an email address and a password.

The JSON identity document managed by this utility is encrypted, and a password must be used to retrieve the document.
By default, the retrieval password is the same as the Cognito credentials password. However, a separate retrieval
password can be specified (in order, for example, to standardise the retrieval password across multiple Cognito
credentials.

The password must be specified when the credentials are created and is required when the credentials are accessed.

SYNOPSIS
cognito_user_credentials.py [{ -l | [-c CREDENTIALS] [{ -s | -t | -d }] }] [-v]

EXAMPLES
./cognito_user_credentials.py -s

FILES
~/SCS/aws/cognito_user_credentials.json

DOCUMENT EXAMPLE
{"email": "production@southcoastscience.com", "password": "scs_admin_Password_123!", "retrieval-password": "beloff"}

SEE ALSO
scs_analysis/cognito_identity

RESOURCES
https://stackoverflow.com/questions/42568262/how-to-encrypt-text-with-a-password-in-python
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_user_credentials import CmdCognitoUserCredentials

from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials, CognitoUserIdentity

from scs_core.data.datum import Datum
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

        cmd = CmdCognitoUserCredentials()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('cognito_user_credentials', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.list:
            for conf_name in CognitoUserCredentials.list(Host):
                print(conf_name, file=sys.stderr)
            exit(0)

        if cmd.set:
            credentials = CognitoUserCredentials.from_user(cmd.credentials_name)

            if not Datum.is_email_address(credentials.email):
                logger.error("The email address is not valid.")
                exit(1)

            if not CognitoUserIdentity.is_valid_password(credentials.password):
                logger.error("The password must include lower and upper case, numeric and punctuation characters.")
                exit(1)

            credentials.save(Host, encryption_key=credentials.retrieval_password)

        elif cmd.test:
            manager = CognitoLoginManager(requests)

            credentials = load_credentials(cmd.credentials_name)

            if credentials is None:
                logger.error("no credentials are available")
                exit(1)

            logger.info(credentials)

            auth = manager.user_login(credentials)
            logger.info("auth: %s" % auth)

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
            print(JSONify.dumps(credentials, indent=cmd.is_valid()))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
