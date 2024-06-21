#!/usr/bin/env python3

"""
Created on 22 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_user_credentials utility is used to manage the AWS Cognito credentials on the user's computer. The
credentials are composed of an email address and a password. The password must be specified when the credentials are
created and is required when the credentials are accessed.

The JSON identity document managed by this utility is encrypted, and a password must be used to retrieve the document.
By default, the retrieval password is the same as the Cognito credentials password. However, a separate retrieval
password can be specified (in order, for example, to standardise the retrieval password across multiple Cognito
accounts).

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
cognito_user_credentials.py [{ -l | [-c CREDENTIALS] [{ -s | -p | -t | -d }] }] [-v]

EXAMPLES
./cognito_user_credentials.py -s

FILES
~/SCS/aws/cognito_user_credentials.json

DOCUMENT EXAMPLE
{"email": "production@southcoastscience.com", "password": "###", "retrieval-password": "###"}

SEE ALSO
scs_analysis/cognito_user_identity

RESOURCES
https://stackoverflow.com/questions/42568262/how-to-encrypt-text-with-a-password-in-python
"""

import sys

from scs_analysis.cmd.cmd_cognito_user_credentials import CmdCognitoUserCredentials

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserIdentity

from scs_core.client.http_exception import HTTPException

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


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
        # authentication...

        if not (cmd.list or cmd.set or cmd.delete):
            credentials = CognitoClientCredentials.load_for_user(Host, name=cmd.credentials_name)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.list:
            for conf_name in sorted(CognitoClientCredentials.list(Host)):
                print(conf_name, file=sys.stderr)
            exit(0)

        elif cmd.set:
            credentials = CognitoClientCredentials.from_user(cmd.credentials_name)

            if not Datum.is_email_address(credentials.email):
                logger.error("The email address is not valid.")
                exit(1)

            if not CognitoUserIdentity.is_valid_password(credentials.password):
                logger.error("The password must include lower and upper case, numeric and punctuation characters.")
                exit(1)

            credentials.save(Host, encryption_key=credentials.retrieval_password)

        elif cmd.update_password:
            if credentials is None:
                logger.error("credentials not found.")
                exit(1)

            credentials = CognitoClientCredentials.from_user(cmd.credentials_name, existing_email=credentials.email)

            if not Datum.is_email_address(credentials.email):
                logger.error("The email address is not valid.")
                exit(1)

            if not CognitoUserIdentity.is_valid_password(credentials.password):
                logger.error("The password must include lower and upper case, numeric and punctuation characters.")
                exit(1)

            credentials.save(Host, encryption_key=credentials.retrieval_password)

        elif cmd.test:
            gatekeeper = CognitoLoginManager()

            if credentials is None:
                logger.error("no credentials are available")
                exit(1)

            logger.info(credentials)

            result = gatekeeper.user_login(credentials)
            logger.error(result.authentication_status.description)

            exit(0 if result.is_ok() else 1)

        elif cmd.delete:
            CognitoClientCredentials.delete(Host)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if credentials:
            print(JSONify.dumps(credentials))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
