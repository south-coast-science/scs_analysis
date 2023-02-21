#!/usr/bin/env python3

"""
Created on 9 Feb 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_password utility is used to

* resend_confirmation - re-send confirmation email when account is created using the API
* resend_temporary_password - re-send temporary password that was created by the security_import system
* request_reset_password - re-send a code needed to do a password reset
* do_reset_password - perform a password reset using the code
* do_set_password - change password when in force reset mode created by security_import system


SYNOPSIS
cognito_password.py { -c EMAIL | -t EMAIL | -r EMAIL | -p EMAIL } [-v]

EXAMPLES
./cognito_password.py -r someone@me.com

SEE ALSO
scs_analysis/cognito_user_credentials
scs_analysis/cognito_user_identity
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_password import CmdCognitoPassword

from scs_core.aws.security.cognito_login_manager import CognitoUserLoginManager, AuthenticationStatus
from scs_core.aws.security.cognito_user import CognitoUserCredentials, CognitoUserIdentity
from scs_core.aws.security.cognito_password_manager import CognitoPasswordManager

from scs_core.data.datum import Datum

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
        # validation...

        if not Datum.is_email_address(cmd.email):
            logger.error("The email address is not valid.")
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        manager = CognitoPasswordManager(requests)
        gatekeeper = CognitoUserLoginManager(requests)

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
            new_password = StdIO.prompt("Enter new password: ")

            if not CognitoUserIdentity.is_valid_password(new_password):
                logger.error("The password must include lower and upper case, numeric and punctuation characters.")
                exit(1)

            manager.do_reset_password(cmd.email, code, new_password)

        if cmd.set_password:
            temporary_password = StdIO.prompt("Enter temporary password: ")

            # login
            credentials = CognitoUserCredentials(None, cmd.email, temporary_password, None)
            auth = gatekeeper.login(credentials)

            if auth.authentication_status != AuthenticationStatus.Challenge:
                logger.error('user not in challenge mode.')
                exit(1)

            new_password = StdIO.prompt("Enter new password: ")

            if not CognitoUserIdentity.is_valid_password(new_password):
                logger.error("The password must include lower and upper case, numeric and punctuation characters.")
                exit(1)

            manager.do_set_password(cmd.email, new_password, auth.content.session)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error("HTTPException: %s" % ex.data)
        exit(1)
