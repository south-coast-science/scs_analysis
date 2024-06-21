#!/usr/bin/env python3

"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The organisation_user_paths utility is used to find, create or delete organisation user paths (OUPs). OUPs
are used to restrict user access:

* If no OUPs are associated with a user, then the user may view all of topics associated with the organisation(s)
that the user is a member of

* If one or more OUP is associated with a user, then the the user may only view the projects identified by the OUPs
within an organisation path root

See the organisation_path_roots utility for more information.

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
organisation_user_paths.py  [-c CREDENTIALS] { -F { -e EMAIL | -r PATH_ROOT } |
-C -e EMAIL -r PATH_ROOT -x PATH_EXTENSION | -D -e EMAIL -r PATH_ROOT -x PATH_EXTENSION } [-i INDENT] [-v]

EXAMPLES
organisation_user_paths.py -i4 -c super -F -e bruno.beloff@southcoastscience.com -r south-coast-science-demo/

DOCUMENT EXAMPLE
{
    "Username": "506cd055-1978-4984-9f17-2fad77797fa1",
    "OPRID": 75,
    "PathExtension": "brighton-urban/"
}

SEE ALSO
scs_analysis/cognito_user_credentials
scs_analysis/organisation_path_roots
"""

import sys

from scs_analysis.cmd.cmd_organisation_user_paths import CmdOrganisationUserPaths

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.aws.security.organisation import OrganisationPathRoot, OrganisationUserPath
from scs_core.aws.security.organisation_manager import OrganisationManager
from scs_core.aws.security.cognito_user_finder import CognitoUserFinder

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.client.http_exception import HTTPException

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    report = []

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

        if cmd.path_root and not OrganisationPathRoot.is_valid_path_root(cmd.path_root):
            logger.error("path root '%s' is not valid." % cmd.path_root)
            exit(2)

        if cmd.path_extension is not None and not OrganisationUserPath.is_valid_path_extension(cmd.path_extension):
            logger.error("path extension '%s' is not valid." % cmd.path_extension)
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

        finder = CognitoUserFinder()
        manager = OrganisationManager()


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        cognito = finder.get_by_email(auth.id_token, cmd.email)

        if cognito is None:
            logger.error("no Cognito user found for email: '%s'." % cmd.email)
            exit(1)

        if cmd.path_root:
            opr = manager.get_opr_by_path_root(auth.id_token, cmd.path_root)

            if opr is None:
                logger.error("no organisation path root found for path: '%s'." % cmd.path_root)
                exit(1)

            opr_id = opr.opr_id

        else:
            opr_id = None


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            report = manager.find_oups(auth.id_token, username=cognito.username, opr_id=opr_id)

        if cmd.create:
            report = OrganisationUserPath(cognito.username, opr_id, cmd.path_extension)
            manager.assert_oup(auth.id_token, report)

        if cmd.delete:
            oup = OrganisationUserPath(cognito.username, opr_id, cmd.path_extension)
            manager.delete_oup(auth.id_token, oup)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if not cmd.delete:
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
