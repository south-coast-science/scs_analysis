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
scs_analysis/cognito_devices
scs_analysis/organisation_users

RESOURCES
https://docs.aws.amazon.com/cognito/latest/developerguide/signing-up-users-in-your-app.html
https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-policies.html
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_users import CmdCognitoUsers

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_membership import CognitoMembership
from scs_core.aws.security.cognito_user import CognitoUserIdentity
from scs_core.aws.security.cognito_user_finder import CognitoUserFinder
from scs_core.aws.security.cognito_user_manager import CognitoUserCreator, CognitoUserEditor, CognitoUserDeleter

from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.client.http_exception import HTTPException, HTTPConflictException

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
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
        # authentication...

        if not cmd.create:
            credentials = CognitoClientCredentials.load_for_user(Host, name=cmd.credentials_name)

            if not credentials:
                exit(1)

            gatekeeper = CognitoLoginManager(requests)
            auth = gatekeeper.user_login(credentials)

            if not auth.is_ok():
                logger.error("login: %s" % auth.authentication_status.description)
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not cmd.create:
            finder = CognitoUserFinder(requests)

        manager = OrganisationManager(requests)

        if cmd.org_label:
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

            if cmd.memberships:
                org_users = manager.find_users(auth.id_token)
                report = CognitoMembership.merge(report, org_users)

        if cmd.create:
            # create...
            if not Datum.is_email_address(cmd.email):
                logger.error("The email address '%s' is not valid." % cmd.email)
                exit(1)

            identity = CognitoUserIdentity(None, None, None, True,
                                           False, cmd.email, cmd.given_name, cmd.family_name, None,
                                           False, False, None)

            manager = CognitoUserCreator(requests)
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

            new_identity = CognitoUserIdentity(identity.username, None, None, enabled,
                                               identity.email_verified, email, given_name, family_name, None,
                                               identity.is_super, identity.is_tester, None)

            auth = gatekeeper.user_login(credentials)                          # renew credentials
            manager = CognitoUserEditor(requests, auth.id_token)
            report = manager.update(new_identity)

        if cmd.delete:
            # TODO: delete user from organisations?
            manager = CognitoUserDeleter(requests, auth.id_token)
            manager.delete(cmd.delete)


        # ------------------------------------------------------------------------------------------------------------
        # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.find:
            logger.info("found: %s" % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPConflictException as ex:
        logger.error("the email address '%s' is already in use." % cmd.email)
        exit(1)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)
