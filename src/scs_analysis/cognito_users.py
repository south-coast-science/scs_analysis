#!/usr/bin/env python3

"""
Created on 24 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_users utility is used to create, update and retrieve AWS Cognito identities. This utility can only be used
by organisation administrators and superusers.

If the --Create function is used, an email is sent to the new user. The verification link in the email must be
excercised in order for the account to gain a CONFIRMED status.

SYNOPSIS
cognito_users.py  [-c CREDENTIALS] { -F [{ -e EMAIL_ADDR | -l ORG_LABEL | -c CONFIRMATION | -s { 1 | 0 } } }] | \
-C | -U -e EMAIL_ADDR | -D -e EMAIL_ADDR } [-i INDENT] [-v]

EXAMPLES
cognito_users.py -Fe bruno.beloff@southcoastscience.com

DOCUMENT EXAMPLE
{"username": "8", "creation-date": "2021-11-24T12:51:12Z", "confirmation-status": "CONFIRMED", "enabled": true,
"email": "bruno.beloff@southcoastscience.com", "given-name": "Bruno", "family-name": "Beloff", "is-super": true}

SEE ALSO
scs_analysis/cognito_credentials

RESOURCES
https://docs.aws.amazon.com/cognito/latest/developerguide/signing-up-users-in-your-app.html
https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-policies.html
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_users import CmdCognitoUsers

from scs_core.aws.security.cognito_account_manager import CognitoCreateManager, CognitoUpdateManager, \
    CognitoDeleteManager

from scs_core.aws.security.cognito_finder import CognitoFinder
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials, CognitoUserIdentity

from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException, HTTPConflictException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    gatekeeper = None
    credentials = None
    auth = None
    finder = None
    manager = None
    org = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCognitoUsers()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('cognito_users', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # auth...

        if not cmd.create:
            gatekeeper = CognitoLoginManager(requests)

            # CognitoUserCredentials...
            if not CognitoUserCredentials.exists(Host, name=cmd.credentials_name):
                logger.error("Cognito credentials not available.")
                exit(1)

            try:
                password = CognitoUserCredentials.password_from_user()
                credentials = CognitoUserCredentials.load(Host, name=cmd.credentials_name, encryption_key=password)
            except (KeyError, ValueError):
                logger.error("incorrect password")
                exit(1)

            try:
                auth = gatekeeper.login(credentials)

            except HTTPException as ex:
                logger.error(ex.data)
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not cmd.create:
            finder = CognitoFinder(requests)

        if cmd.org_label:
            manager = OrganisationManager(requests)
            org = manager.get_organisation_by_label(auth.id_token, cmd.org_label)

            if org is None:
                logger.error("no organisation found for label: '%s'." % cmd.org_label)
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            if cmd.email is not None:
                report = sorted(finder.find_by_email(auth.id_token, cmd.email))

            elif cmd.org_label is not None:
                org_users = manager.find_users_by_organisation(auth.id_token, org.org_id)
                usernames = [org_user.username for org_user in org_users]

                report = sorted(finder.find_by_usernames(auth.id_token, usernames))

            elif cmd.confirmation_status is not None:
                report = sorted(finder.find_by_status(auth.id_token,
                                                      CognitoUserIdentity.status(cmd.confirmation_status)))

            elif cmd.enabled is not None:
                report = sorted(finder.find_by_enabled(auth.id_token, cmd.enabled))

            else:
                report = sorted(finder.find_all(auth.id_token))

        if cmd.create:
            # create...
            if not Datum.is_email_address(cmd.email):
                logger.error("The email address '%s' is not valid." % cmd.email)
                exit(1)

            # if not CognitoUserIdentity.is_valid_password(password):
            #     logger.error("The password '%s' is not valid." % password)
            #     exit(1)

            identity = CognitoUserIdentity(None, None, None, None,
                                           cmd.email, cmd.given_name, cmd.family_name, None)

            manager = CognitoCreateManager(requests)
            report = manager.create(identity)

        if cmd.update:
            # find...
            identity = finder.get_by_email(auth.id_token, cmd.update)

            if identity is None:
                logger.error("no identity found for email: '%s'." % cmd.update)
                exit(1)

            # update...
            enabled = identity.enabled if cmd.enabled is None else cmd.enabled
            email = identity.email if cmd.email is None else cmd.email
            given_name = identity.given_name if cmd.given_name is None else cmd.given_name
            family_name = identity.family_name if cmd.family_name is None else cmd.family_name

            if not Datum.is_email_address(email):
                logger.error("The email address '%s' is not valid." % email)
                exit(1)

            # if password and not CognitoUserIdentity.is_valid_password(password):
            #     logger.error("The password '%s' is not valid." % password)
            #     exit(1)

            report = CognitoUserIdentity(identity.username, None, None,
                                         enabled, email, given_name, family_name, None)

            auth = gatekeeper.login(credentials)                          # renew credentials
            manager = CognitoUpdateManager(requests, auth.id_token)
            manager.update(identity)

        if cmd.delete:
            # TODO: delete user from organisations
            manager = CognitoDeleteManager(requests, auth.id_token)
            manager.delete(cmd.delete)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPConflictException as ex:
        logger.error("the email address '%s' is already in use." % report.email)
        exit(1)
