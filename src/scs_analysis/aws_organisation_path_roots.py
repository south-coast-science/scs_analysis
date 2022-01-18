#!/usr/bin/env python3

"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_organisation_path_roots utility is used to

SYNOPSIS
aws_organisation_path_roots.py  { -F ORG_LABEL | -C ORG_LABEL PATH_ROOT | -D ORG_LABEL PATH_ROOT } [-i INDENT] [-v]

EXAMPLES
aws_organisation_path_roots.py -F NARA

DOCUMENT EXAMPLE
{"OPRID": 11, "OrgID": 1, "PathRoot": "ricardo/"}

SEE ALSO
scs_analysis/cognito_credentials
"""

import requests
import sys

from scs_analysis.cmd.cmd_aws_organisation_path_roots import CmdAWSOrganisationPathRoots

from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials

from scs_core.aws.security.organisation import OrganisationPathRoot
from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    credentials = None
    authentication = None
    org = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdAWSOrganisationPathRoots()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('aws_organisation_path_roots', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)

        if cmd.create_path_root is not None and not OrganisationPathRoot.is_valid_path_root(cmd.create_path_root):
            logger.error("the path root '%s' is not valid." % cmd.create_path_root)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        gatekeeper = CognitoLoginManager(requests)

        # CognitoUserCredentials...
        if not CognitoUserCredentials.exists(Host):
            logger.error("Cognito credentials not available.")
            exit(1)

        try:
            password = CognitoUserCredentials.password_from_user()
            credentials = CognitoUserCredentials.load(Host, encryption_key=password)
        except (KeyError, ValueError):
            logger.error("incorrect password")
            exit(1)

        try:
            authentication = gatekeeper.login(credentials)

        except HTTPException as ex:
            logger.error(ex.data)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        manager = OrganisationManager(requests)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            # validate...
            org = manager.get_organisation_by_label(authentication.id_token, cmd.find)

            if org is None:
                logger.error("no organisation found for label: '%s'." % cmd.find)
                exit(1)

            # find...
            report = manager.find_oprs_by_organisation(authentication.id_token, org.org_id)

        if cmd.create:
            # validate...
            org = manager.get_organisation_by_label(authentication.id_token, cmd.create_org_label)

            if org is None:
                logger.error("no organisation found for label: '%s'." % cmd.create_org_label)
                exit(1)

            org = OrganisationPathRoot(0, org.org_id, cmd.create_path_root)
            report = manager.insert_opr(authentication.id_token, org)

        if cmd.delete:
            # validate...
            org = manager.get_organisation_by_label(authentication.id_token, cmd.delete_org_label)

            if org is None:
                logger.error("no organisation found for label: '%s'." % cmd.delete_org_label)
                exit(1)

            opr = manager.get_opr_by_organisation_path_root(authentication.id_token, org.org_id, cmd.delete_path_root)

            if opr is None:
                logger.error("no path root found for label: '%s' and path root: '%s'." %
                             (cmd.delete_org_label, cmd.delete_path_root))
                exit(1)

            # delete...
            manager.delete_opr(authentication.id_token, cmd.delete)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
