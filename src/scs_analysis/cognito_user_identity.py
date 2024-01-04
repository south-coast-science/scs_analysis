#!/usr/bin/env python3

"""
Created on 24 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_user_identity utility is used to create, update and retrieve the AWS Cognito identity for the user.

If the --Create function is used, an email is sent to the new user. The verification link in the email must be
excercised in order for the account to gain a CONFIRMED status.

SYNOPSIS
cognito_user_identity.py [-c CREDENTIALS] | -C | -R | -U } [-i INDENT] [-v]

EXAMPLES
./cognito_user_identity.py -R

DOCUMENT EXAMPLE
{"username": "506cd055-1978-4984-9f17-2fad77797fa1", "email": "bruno.beloff@southcoastscience.com",
"given-name": "Bruno", "family-name": "Beloff", "confirmation-status": "CONFIRMED", "enabled": true,
"email-verified": true, "is-super": true, "is-tester": true, "is-financial": true,
"created": "2023-04-20T11:45:21Z", "last-updated": "2023-06-26T14:39:17Z"}

SEE ALSO
scs_analysis/cognito_user_credentials

RESOURCES
https://docs.aws.amazon.com/cognito/latest/developerguide/signing-up-users-in-your-app.html
https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-policies.html
"""

import sys

from scs_analysis.cmd.cmd_cognito_user_identity import CmdCognitoUserIdentity

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserIdentity
from scs_core.aws.security.cognito_user_finder import CognitoUserFinder
from scs_core.aws.security.cognito_user_manager import CognitoUserCreator, CognitoUserEditor

from scs_core.client.http_exception import HTTPException, HTTPConflictException

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.comms.stdio import StdIO
from scs_host.sys.host import Host


# TODO: check for newlines on interactivity
# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    gatekeeper = None
    credentials = None
    auth = None
    finder = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCognitoUserIdentity()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('cognito_user_identity', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        if not cmd.create:
            credentials = CognitoClientCredentials.load_for_user(Host, name=cmd.credentials_name)

            if not credentials:
                exit(1)

            gatekeeper = CognitoLoginManager()
            auth = gatekeeper.user_login(credentials)

            if not auth.is_ok():
                logger.error("login: %s." % auth.authentication_status.description)
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not cmd.create:
            finder = CognitoUserFinder()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.retrieve:
            report = finder.get_self(auth.id_token)

        if cmd.create:
            # create...
            given_name = StdIO.prompt("Enter given name")
            family_name = StdIO.prompt("Enter family name")
            email = StdIO.prompt("Enter email address")
            password = StdIO.prompt("Enter password")
            retrieval_password = StdIO.prompt("Enter retrieval password (RETURN for same)")

            if not retrieval_password:
                retrieval_password = password

            # validation...
            if not given_name or not given_name:
                logger.error("Given name and family name are required.")
                exit(1)

            if not Datum.is_email_address(email):
                logger.error("The email address is not valid.")
                exit(1)

            if not CognitoUserIdentity.is_valid_password(password):
                logger.error("The password must include lower and upper case, numeric and punctuation characters.")
                exit(1)

            # save identity...
            identity = CognitoUserIdentity(None, None, None, True, False, email,
                                           given_name, family_name, password, False, False, False, None)

            manager = CognitoUserCreator()
            report = manager.create(identity)

            # create credentials...
            credentials = CognitoClientCredentials(cmd.credentials_name, email, password, retrieval_password)
            credentials.save(Host, encryption_key=retrieval_password)

        if cmd.update:
            # find...
            identity = finder.get_self(auth.id_token)

            # update identity...
            given_name = StdIO.prompt("Enter given name", default=identity.given_name)
            family_name = StdIO.prompt("Enter family name", default=identity.family_name)
            email = StdIO.prompt("Enter email address", default=identity.email)
            password = StdIO.prompt("Enter password (RETURN to keep existing)")

            if not password:
                password = credentials.password

            if credentials.retrieval_password == credentials.password:
                retrieval_password = StdIO.prompt("Enter retrieval password (RETURN for same)")

                if not retrieval_password:
                    retrieval_password = password

            else:
                retrieval_password = StdIO.prompt("Enter retrieval password (RETURN to keep existing)")

                if not retrieval_password:
                    retrieval_password = credentials.retrieval_password

            # validation...
            if not given_name or not given_name:
                logger.error("Given name and family name are required.")
                exit(1)

            if not Datum.is_email_address(email):
                logger.error("The email address '%s' is not valid." % email)
                exit(1)

            if password and not CognitoUserIdentity.is_valid_password(password):
                logger.error("The password '%s' is not valid." % password)
                exit(1)

            # save identity...
            identity = CognitoUserIdentity(identity.username, None, None, True, identity.email_verified, email,
                                           given_name, family_name, password, identity.is_super, identity.is_tester,
                                           identity.is_financial, None)

            auth = gatekeeper.user_login(credentials)                          # renew credentials
            manager = CognitoUserEditor()
            report = manager.update(auth.id_token, identity)

            # update credentials...
            credentials = CognitoClientCredentials(credentials.name, email, password, retrieval_password)
            credentials.save(Host, encryption_key=retrieval_password)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPConflictException as ex:
        logger.error("the email address '%s' is already in use." % report.email)
        exit(1)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
