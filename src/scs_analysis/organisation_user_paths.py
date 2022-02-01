#!/usr/bin/env python3

"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The organisation_user_paths utility is used to

SYNOPSIS
organisation_user_paths.py  [-c CREDENTIALS] { -F -e EMAIL -r PATH_ROOT | \
-C -e EMAIL -r PATH_ROOT -x PATH_EXTENSION | \
-D -e EMAIL -r PATH_ROOT -x PATH_EXTENSION } \
[-i INDENT] [-v]

EXAMPLES
organisation_user_paths.py -F -u NARA

DOCUMENT EXAMPLE
{"Username": 111, "OrgID": 1, "IsOrgAdmin": true, "IsDeviceAdmin": true, "IsSuspended": false}

SEE ALSO
scs_analysis/cognito_credentials
"""

import requests
import sys

from scs_analysis.cmd.cmd_organisation_user_paths import CmdOrganisationUserPaths

from scs_core.aws.security.cognito_finder import CognitoFinder
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials

from scs_core.aws.security.organisation import OrganisationPathRoot, OrganisationUserPath
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

        cmd = CmdOrganisationUserPaths()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('organisation_user_paths', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)

        if not Datum.is_email_address(cmd.email):
            logger.error("email address '%s' is not valid." % cmd.email)
            exit(2)

        if not OrganisationPathRoot.is_valid_path_root(cmd.path_root):
            logger.error("path root '%s' is not valid." % cmd.path_root)
            exit(2)

        if cmd.path_extension is not None and not OrganisationUserPath.is_valid_path_extension(cmd.path_extension):
            logger.error("path extension '%s' is not valid." % cmd.path_extension)
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

        cognito = finder.get_by_email(auth.id_token, cmd.email)

        if cognito is None:
            logger.error("no Cognito user found for email: '%s'." % cmd.email)
            exit(1)

        opr = manager.get_opr_by_path_root(auth.id_token, cmd.path_root)

        if opr is None:
            logger.error("no organisation path root found for path: '%s'." % cmd.path_root)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            report = manager.find_oups(auth.id_token, cognito.username, opr.opr_id)

        if cmd.create:
            report = OrganisationUserPath(cognito.username, opr.opr_id, cmd.path_extension)
            manager.assert_oup(auth.id_token, report)

        if cmd.delete:
            oup = OrganisationUserPath(cognito.username, opr.opr_id, cmd.path_extension)
            manager.delete_oup(auth.id_token, oup)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
