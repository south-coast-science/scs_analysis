#!/usr/bin/env python3

"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The organisation_users utility is used to

SYNOPSIS
organisation_users.py  [-c CREDENTIALS] { -F { -e EMAIL | -l ORG_LABEL } | \
-R -e EMAIL -l ORG_LABEL | \
-C -e EMAIL -l ORG_LABEL -o { 1 | 0 } -d { 1 | 0 } | \
-U -e EMAIL -l ORG_LABEL [-o { 1 | 0 }] [-d { 1 | 0 }] [-s { 1 | 0 }] | \
-D -e EMAIL -l ORG_LABEL } \
[-i INDENT] [-v]

EXAMPLES
organisation_users.py -F -l NARA

DOCUMENT EXAMPLE
{"Username": 111, "OrgID": 1, "IsOrgAdmin": true, "IsDeviceAdmin": true, "IsSuspended": false}

SEE ALSO
scs_analysis/cognito_credentials
"""

import requests
import sys

from scs_analysis.cmd.cmd_organisation_users import CmdOrganisationUsers

from scs_core.aws.security.cognito_finder import CognitoFinder
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials

from scs_core.aws.security.organisation import OrganisationUser
from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    credentials = None
    auth = None
    cognito = None
    org = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdOrganisationUsers()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('organisation_users', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)

        if cmd.email is not None and not Datum.is_email_address(cmd.email):
            logger.error("email address '%s' is not valid." % cmd.email)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # auth...

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

        finder = CognitoFinder(requests)
        manager = OrganisationManager(requests)


        # ------------------------------------------------------------------------------------------------------------
        # validate...

        if cmd.email:
            cognito = finder.get_by_email(auth.id_token, cmd.email)

            if cognito is None:
                logger.error("no Cognito user found for email: '%s'." % cmd.email)
                exit(1)

        if cmd.org_label:
            org = manager.get_organisation_by_label(auth.id_token, cmd.org_label)

            if org is None:
                logger.error("no organisation found for label: '%s'." % cmd.org_label)
                exit(1)

        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            if cmd.email:
                report = manager.find_users_by_username(auth.id_token, cognito.username)
            else:
                report = manager.find_users_by_organisation(auth.id_token, org.org_id)

        if cmd.retrieve:
            report = manager.get_user(auth.id_token, cognito.username, org.org_id)

        if cmd.create:
            is_org_admin = cmd.org_admin == 1
            is_device_admin = cmd.device_admin == 1
            is_suspended = False

            report = OrganisationUser(cognito.username, org.org_id, is_org_admin, is_device_admin, is_suspended)
            manager.assert_user(auth.id_token, report)

        if cmd.update:
            user = manager.get_user(auth.id_token, cognito.username, org.org_id)

            if user is None:
                logger.error("no organisation user found for email: '%s' and label '%s'." % (cmd.email, cmd.org_label))
                exit(1)

            is_org_admin = user.is_org_admin if cmd.org_admin is None else bool(cmd.org_admin)
            is_device_admin = user.is_device_admin if cmd.device_admin is None else bool(cmd.device_admin)
            is_suspended = user.is_suspended if cmd.suspended is None else bool(cmd.suspended)

            report = OrganisationUser(cognito.username, org.org_id, is_org_admin, is_device_admin, is_suspended)
            manager.assert_user(auth.id_token, report)

        if cmd.delete:
            manager.delete_user(auth.id_token, cognito.username, org.org_id)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
