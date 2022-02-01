#!/usr/bin/env python3

"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The organisation_path_roots utility is used to

SYNOPSIS
organisation_path_roots.py  [-c CREDENTIALS] { -F -l ORG_LABEL | \
-C -l ORG_LABEL -r PATH_ROOT | \
-D -l ORG_LABEL -r PATH_ROOT } \
[-i INDENT] [-v]

EXAMPLES
organisation_path_roots.py -F -l NARA

DOCUMENT EXAMPLE
{"OPRID": 11, "OrgID": 1, "PathRoot": "ricardo/"}

SEE ALSO
scs_analysis/cognito_credentials
"""

import requests
import sys

from scs_analysis.cmd.cmd_organisation_path_roots import CmdOrganisationPathRoots

from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials

from scs_core.aws.security.organisation import Organisation, OrganisationPathRoot
from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    credentials = None
    auth = None
    org = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdOrganisationPathRoots()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('organisation_path_roots', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)

        if not Organisation.is_valid_label(cmd.org_label):
            logger.error("the organisation label '%s' is not valid." % cmd.org_label)
            exit(2)

        if cmd.path_root is not None and not OrganisationPathRoot.is_valid_path_root(cmd.path_root):
            logger.error("the path root '%s' is not valid." % cmd.path_root)
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

        manager = OrganisationManager(requests)


        # ------------------------------------------------------------------------------------------------------------
        # validate...

        if cmd.org_label is not None:
            org = manager.get_organisation_by_label(auth.id_token, cmd.org_label)

            if org is None:
                logger.error("no organisation found for label: '%s'." % cmd.org_label)
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            report = manager.find_oprs_by_organisation(auth.id_token, org.org_id)

        if cmd.create:
            org = OrganisationPathRoot(0, org.org_id, cmd.path_root)
            report = manager.insert_opr(auth.id_token, org)

        if cmd.delete:
            opr = manager.get_opr_by_path_root(auth.id_token, cmd.path_root)

            if opr is None:
                logger.error("no path root found for path: '%s'." % cmd.path_root)
                exit(1)

            # delete...
            manager.delete_opr(auth.id_token, cmd.delete)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
