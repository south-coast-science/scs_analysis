#!/usr/bin/env python3

"""
Created on 9 Feb 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_password utility is used to

SYNOPSIS
cognito_password.py { -c EMAIL | -r EMAIL | -p EMAIL } [-v]

EXAMPLES
./cognito_password.py -r someone@me.com

SEE ALSO
scs_analysis/cognito_user_credentials
scs_analysis/cognito_user_identity
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_password import CmdCognitoPassword

from scs_core.aws.security.cognito_user import CognitoUserIdentity
from scs_core.aws.security.cognito_password_manager import CognitoPasswordManager

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.comms.stdio import StdIO


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    credentials = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCognitoPassword()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('cognito_password', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        manager = CognitoPasswordManager(requests)


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        if not Datum.is_email_address(cmd.email):
            logger.error("The email address is not valid.")
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.resend_confirmation:
            manager.resend_confirmation(cmd.email)

        if cmd.resend_temporary:
            manager.resend_temporary_password(cmd.email)

        if cmd.request_reset:
            manager.request_reset_password(cmd.email)

        if cmd.reset_password:
            code = StdIO.prompt("Enter confirmation code: ")
            password = StdIO.prompt("Enter new password: ")

            if not CognitoUserIdentity.is_valid_password(password):
                logger.error("The password must include lower and upper case, numeric and punctuation characters.")
                exit(1)

            manager.do_reset_password(cmd.email, code, password)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
