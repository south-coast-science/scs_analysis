#!/usr/bin/env python3

"""
Created on 10 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The organisations utility is used to find, create, update or delete organisation records.

The utility supports a parent / child relationship between organisations - a child organisation can be
thought of as a subdivision of its parent. Users belonging to an organisation have the same rights over
child organisation data and devices as then have

SYNOPSIS
organisations.py [-c CREDENTIALS] {
-F [-l LABEL] [-m] |
-C -l LABEL -n LONG_NAME -u URL -o OWNER_EMAIL [-p PARENT_LABEL] |
-U LABEL [-l LABEL] [-n LONG_NAME] [-u URL] [-o OWNER_EMAIL] [-p PARENT_LABEL] |
-D LABEL } [-i INDENT] [-v]

EXAMPLES
organisations.py -F

DOCUMENT EXAMPLE
{"OrgID": 1, "Label": "SCS", "LongName": "South Coast Science", "URL": "https://www.southcoastscience.com",
"Owner": "bruno.beloff@southcoastscience.com", "ParentID": null}

DOCUMENT EXAMPLE - MEMBERSHIPS
{"organisation": {"OrgID": 11, "Label": "CEPEMAR", "LongName": "CEPEMAR", "URL": "http://cepemar.com",
"Owner": "felipe.tatagiba@cepemar.com", "ParentID": null}, "children": [
{"OrgID": 82, "Label": "Vale", "LongName": "Vale S.A.", "URL": "http://www.vale.com/",
"Owner": "felipe.tatagiba@cepemar.com", "ParentID": 11}]}

SEE ALSO
scs_analysis/cognito_user_credentials
"""

import sys

from scs_analysis.cmd.cmd_organisations import CmdOrganisations

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.aws.security.organisation import Organisation
from scs_core.aws.security.organisation_manager import OrganisationManager
from scs_core.aws.security.organisation_membership import OrganisationMembership

from scs_core.client.http_exception import HTTPException, HTTPNotFoundException

from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.comms.stdio import StdIO
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdOrganisations()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('organisations', verbose=cmd.verbose)       # level=logging.DEBUG
        logger = Logging.getLogger()

        logger.info(cmd)

        if cmd.label is not None and not Organisation.is_valid_label(cmd.label):
            logger.error("the label '%s' is not valid." % cmd.label)
            exit(2)

        if cmd.long_name is not None and not Organisation.is_valid_long_name(cmd.long_name):
            logger.error("the long name '%s' is not valid." % cmd.long_name)
            exit(2)

        if cmd.url is not None and not Organisation.is_valid_url(cmd.url):
            logger.error("the URL '%s' is not valid." % cmd.url)
            exit(2)

        if cmd.owner is not None and not Organisation.is_valid_owner(cmd.owner):
            logger.error("the owner email address '%s' is not valid." % cmd.owner)
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

        if cmd.parent_label is None or cmd.parent_label == 'none':
            parent_id = None

        else:
            try:
                parent = manager.get_organisation_by_label(auth.id_token, cmd.parent_label)
                parent_id = parent.org_id

            except HTTPNotFoundException:
                logger.error("no organisation found for parent label: '%s'." % cmd.parent_label)
                exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            report = manager.get_organisation_by_label(auth.id_token, cmd.label) if cmd.label else \
                sorted(manager.find_organisations(auth.id_token))

            if cmd.memberships:
                if cmd.label:
                    report = [report]
                    orgs = manager.find_organisations(auth.id_token)
                else:
                    orgs = report

                report = OrganisationMembership.merge(report, orgs)

        if cmd.create:
            org = Organisation(0, cmd.label, cmd.long_name, cmd.url, cmd.owner, parent_id)
            report = manager.insert_organisation(auth.id_token, org)

        if cmd.update:
            # find...
            org = manager.get_organisation_by_label(auth.id_token, cmd.update)

            if org is None:
                logger.error("no organisation found for label: '%s'." % cmd.update)
                exit(1)

            # update...
            label = org.label if cmd.label is None else cmd.label
            long_name = org.long_name if cmd.long_name is None else cmd.long_name
            url = org.url if cmd.url is None else cmd.url
            owner = org.owner if cmd.owner is None else cmd.owner
            parent_id = org.parent_id if cmd.parent_label is None else parent_id

            report = Organisation(org.org_id, label, long_name, url, owner, parent_id)
            manager.update_organisation(auth.id_token, report)

        if cmd.delete:
            # find...
            org = manager.get_organisation_by_label(auth.id_token, cmd.delete)

            if org is None:
                logger.error("no organisation found for label: '%s'" % cmd.delete)
                exit(1)

            # check...
            response = StdIO.prompt('Are you sure? (Y/n)')
            if response != 'Y':
                exit(0)

            # delete...
            manager.delete_organisation(auth.id_token, org.org_id)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.find and not cmd.label:
            logger.info("found: %s" % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
