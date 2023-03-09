#!/usr/bin/env python3

"""
Created on 9 Feb 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_password utility is used to set or reset the user's password, or to request an email to permit
password operations. Which email message is sent depends on the state of the state of the user's account:

* UNCONFIRMED - the account creation email is re-sent
* CONFIRMED - a password reset code is sent and the user account enters the PASSWORD_RESET_REQUIRED state
* PASSWORD_RESET_REQUIRED - a password reset code is re-sent
* FORCE_CHANGE_PASSWORD - the temporary password is re-sent

Emails cannot be sent to users in the DISABLED state.

SYNOPSIS
cognito_password.py { -e | -s | -r } EMAIL [-v]

EXAMPLES
./cognito_password.py -r someone@me.com

SEE ALSO
scs_analysis/cognito_user_credentials
scs_analysis/cognito_user_identity
scs_analysis/cognito_users
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_password import CmdCognitoPassword

from scs_core.aws.security.cognito_login_manager import CognitoLoginManager, AuthenticationStatus
from scs_core.aws.security.cognito_user import CognitoUserCredentials, CognitoUserIdentity
from scs_core.aws.security.cognito_password_manager import CognitoPasswordManager

from scs_core.data.datum import Datum

from scs_core.sys.http_exception import HTTPException, HTTPUnauthorizedException, HTTPNotFoundException
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
        gatekeeper = CognitoLoginManager(requests)


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        if not Datum.is_email_address(cmd.email):
            logger.error("The email address is not valid.")
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.send_email:
            try:
                manager.send_email(cmd.email)
                logger.error("an email has been sent to '%s'." % cmd.email)

            except HTTPUnauthorizedException:
                logger.error("the user '%s' is disabled." % cmd.email)
                exit(1)

            except HTTPNotFoundException:
                logger.error("no user could be found for email '%s'." % cmd.email)
                exit(1)

        if cmd.reset_password:
            code = StdIO.prompt("Enter confirmation code")
            new_password = StdIO.prompt("Enter new password")

            if not CognitoUserIdentity.is_valid_password(new_password):
                logger.error("The password must include lower and upper case, numeric and punctuation characters.")
                exit(1)

            manager.do_reset_password(cmd.email, code, new_password)

        if cmd.set_password:
            temporary_password = StdIO.prompt("Enter temporary password")

            # login
            credentials = CognitoUserCredentials(None, cmd.email, temporary_password, None)
            auth = gatekeeper.user_login(credentials)

            if auth.authentication_status != AuthenticationStatus.Challenge:
                logger.error('user not in challenge mode.')
                exit(1)

            new_password = StdIO.prompt("Enter new password")

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
