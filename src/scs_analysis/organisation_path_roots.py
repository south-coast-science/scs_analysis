#!/usr/bin/env python3

"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The organisation_path_roots utility is used to find, create or delete organisation path roots. Organisation path roots
are the leftmost part of a topic path. For example, in:

south-coast-science-demo/brighton-urban/loc/1/climate

the organisation path root is south-coast-science-demo/. In the security system, organisation path roots are used to
maintain a mapping between topics and organisations.

The members of an organisation path root are the organisation user paths (OUPs) that restrict access to specific users.
See the organisation_user_paths utility for more information.

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
organisation_path_roots.py  [-c CREDENTIALS] { -F [-l ORG_LABEL [-m]] | -C -l ORG_LABEL -r PATH_ROOT |
-D -l ORG_LABEL -r PATH_ROOT } [-i INDENT] [-v]

EXAMPLES
organisation_path_roots.py -vi4 -c super -Fl "South Coast Science (Demo)" -m

DOCUMENT EXAMPLE
[
    {
        "OPRID": 75,
        "OrgID": 68,
        "PathRoot": "south-coast-science-demo/"
    }
]

DOCUMENT EXAMPLE - MEMBERSHIPS
[
    {
        "opr": {
            "OPRID": 75,
            "OrgID": 68,
            "PathRoot": "south-coast-science-demo/"
        },
        "memberships": [
            {
                "Username": "506cd055-1978-4984-9f17-2fad77797fa1",
                "OPRID": 75,
                "PathExtension": "brighton-urban/"
            }
        ]
    }
]

SEE ALSO
scs_analysis/cognito_user_credentials
scs_analysis/organisation_user_paths
"""

import sys

from scs_analysis.cmd.cmd_organisation_path_roots import CmdOrganisationPathRoots

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.aws.security.organisation import Organisation, OrganisationPathRoot
from scs_core.aws.security.organisation_manager import OrganisationManager
from scs_core.aws.security.opr_membership import OPRMembership

from scs_core.client.http_exception import HTTPException

from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
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

        if cmd.org_label is not None and not Organisation.is_valid_label(cmd.org_label):
            logger.error("the organisation label '%s' is not valid." % cmd.org_label)
            exit(2)

        if cmd.path_root is not None and not OrganisationPathRoot.is_valid_path_root(cmd.path_root):
            logger.error("the path root '%s' is not valid." % cmd.path_root)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

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

        manager = OrganisationManager()


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        if cmd.org_label is not None:
            org = manager.get_organisation_by_label(auth.id_token, cmd.org_label)

            if org is None:
                logger.error("no organisation found for label: '%s'." % cmd.org_label)
                exit(1)

            org_id = org.org_id

        else:
            org_id = None


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            report = manager.find_oprs(auth.id_token, org_id=org_id)

            if report and cmd.memberships:
                oups = manager.find_oups(auth.id_token, opr_id=report[0].opr_id)
                report = OPRMembership.merge(report, oups)

        if cmd.create:
            org = OrganisationPathRoot(0, org.org_id, cmd.path_root)
            report = manager.insert_opr(auth.id_token, org)

        if cmd.delete:
            opr = manager.get_opr_by_path_root(auth.id_token, cmd.path_root)

            if opr is None:
                logger.error("no path root found for path: '%s'." % cmd.path_root)
                exit(1)

            # delete...
            manager.delete_opr(auth.id_token, opr.opr_id)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.find:
            logger.info("found: %s" % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
