#!/usr/bin/env python3

"""
Created on 22 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito utility is used to manage the AWS Cognito credentials for the user. The credentials are composed of an
email address and a password. The JSON identity document managed by this utility is encrypted.

The password must be specified when the credentials are created and is required when the credentials are accessed.

SYNOPSIS
cognito.py [{ -s | -d }] [-v]

EXAMPLES
./cognito.py -s

FILES
~/SCS/aws/cognito_user_credentials.json

DOCUMENT EXAMPLE
{"email-address": "bruno.beloff@southcoastscience.com", "password": "hello"}

SEE ALSO

RESOURCES
https://stackoverflow.com/questions/42568262/how-to-encrypt-text-with-a-password-in-python
"""

import sys

from scs_analysis.cmd.cmd_cognito import CmdCognito

from scs_core.aws.client.cognito_user_credentials import CognitoUserCredentials
from scs_core.data.json import JSONify
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    credentials = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCognito()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('cognito', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.set:
            credentials = CognitoUserCredentials.from_user()

            if not credentials.ok():
                logger.error("the identity is not valid")
                exit(1)

            credentials.save(Host, encryption_key=credentials.password)

        elif cmd.delete:
            CognitoUserCredentials.delete(Host)

        else:
            password = CognitoUserCredentials.password_from_user()

            try:
                credentials = CognitoUserCredentials.load(Host, encryption_key=password)
            except (KeyError, ValueError):
                logger.error("incorrect password")
                exit(1)

        if credentials:
            print(JSONify.dumps(credentials))

    except KeyboardInterrupt:
        print(file=sys.stderr)
