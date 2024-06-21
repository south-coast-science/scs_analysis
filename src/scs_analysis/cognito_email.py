#!/usr/bin/env python3

"""
Created on 9 Feb 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_email utility is used to set or reset the user's password, or to request an email to permit
password operations. Which email message is sent depends on the state of the state of the user's account:

* UNCONFIRMED - the account creation email is re-sent
* CONFIRMED - a password reset code is sent and the user account enters the PASSWORD_RESET_REQUIRED state
* PASSWORD_RESET_REQUIRED - a password reset code is re-sent
* FORCE_CHANGE_PASSWORD - the temporary password is re-sent

Emails cannot be sent to users in the DISABLED state.

When an email is received, the cognito_email utility should be used to process the response, which is one of:

* Confirm account - using the emailed confirmation code
* Set password - using the emailed temporary password
* Reset password - using the emailed reset code

SYNOPSIS
cognito_email.py { -e | -c | -s | -r } [-v] EMAIL

EXAMPLES
cognito_email.py -r someone@me.com

SEE ALSO
scs_analysis/cognito_user_credentials
scs_analysis/cognito_user_identity
scs_analysis/cognito_users
"""

import sys

from scs_analysis.cmd.cmd_cognito_email import CmdCognitoEmail

from scs_core.aws.security.cognito_authentication import AuthenticationStatus
from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_password_manager import CognitoPasswordManager
from scs_core.aws.security.cognito_user import CognitoUserIdentity
from scs_core.aws.security.cognito_user_manager import CognitoUserCreator

from scs_core.client.http_exception import HTTPException, HTTPBadRequestException, HTTPGoneException, \
    HTTPNotFoundException, HTTPNotAllowedException, HTTPUnauthorizedException

from scs_core.data.datum import Datum

from scs_core.sys.logging import Logging

from scs_host.comms.stdio import StdIO
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

def do_password(do_set):
    new_password = StdIO.prompt("Enter new password")

    if not CognitoUserIdentity.is_valid_password(new_password):
        logger.error("The password must include lower and upper case, numeric and punctuation characters.")
        exit(1)

    try:
        if do_set:
            password_manager.do_set_password(cmd.email, new_password, auth.content.session)
        else:
            password_manager.do_reset_password(cmd.email, code, new_password)

    except HTTPNotFoundException:
        logger.error("no user could be found for email '%s'." % cmd.email)
        exit(1)

    except HTTPUnauthorizedException:
        logger.error("the user '%s' is disabled." % cmd.email)
        exit(1)

    except HTTPNotAllowedException:
        alternative = '--reset-password' if do_set else '--set-password'
        logger.error("the operation is not permitted in the current user state. Try %s?" % alternative)
        exit(1)

    except HTTPBadRequestException as error:
        if error.data == "Mismatch":
            logger.error("the code '%s' is not valid." % code)
            exit(1)

        if error.data == "Expired":
            logger.error("the code has expired.")
            exit(1)

        logger.error(repr(ex))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCognitoEmail()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('cognito_email', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)
        logger.debug(Host)              # initialise API endpoint reporting

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        password_manager = CognitoPasswordManager()
        user_manager = CognitoUserCreator()
        gatekeeper = CognitoLoginManager()


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        if not Datum.is_email_address(cmd.email):
            logger.error("The email address is not valid.")
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.send_email:
            try:
                password_manager.send_email(cmd.email)
                logger.error("an email has been sent.")
                exit(0)

            except HTTPUnauthorizedException:
                logger.error("the user '%s' is disabled." % cmd.email)
                exit(1)

            except HTTPNotFoundException:
                logger.error("no user could be found for email '%s'." % cmd.email)
                exit(2)

        if cmd.confirm:
            confirmation_code = StdIO.prompt("Enter confirmation code")

            try:
                user_manager.confirm(cmd.email, confirmation_code)
                logger.error("OK")
                exit(0)

            except HTTPNotFoundException:
                logger.error("no user could be found for email '%s'." % cmd.email)
                exit(2)

            except HTTPGoneException:
                logger.error("the account has already been confirmed.")
                exit(1)

        if cmd.set_password:
            temporary_password = StdIO.prompt("Enter temporary password")

            # login
            credentials = CognitoClientCredentials(None, cmd.email, temporary_password, None)
            auth = gatekeeper.user_login(credentials)

            if auth.authentication_status != AuthenticationStatus.Challenge:
                logger.error(auth.authentication_status.description)
                exit(1)

            do_password(True)
            logger.error("the password has been set.")
            exit(0)

        if cmd.reset_password:
            code = StdIO.prompt("Enter verification code")

            do_password(False)
            logger.error("the password has been reset - update your stored credentials.")
            exit(0)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
