#!/usr/bin/env python3

"""
Created on 10 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_organisations utility is used to

SYNOPSIS
aws_organisations.py  { -F | -R LABEL | -C -l LABEL -n LONG_NAME -u URL -o OWNER_EMAIL | \
-U LABEL [-l LABEL] [-n LONG_NAME] [-u URL] [-o OWNER_EMAIL] | -D LABEL } [-i INDENT] [-v]

EXAMPLES
aws_organisations.py -F

DOCUMENT EXAMPLE
{"OrgID": 1, "Label": "SCS", "LongName": "South Coast Science", "URL": "https://www.southcoastscience.com",
"Owner": "bruno.beloff@southcoastscience.com"}

SEE ALSO
scs_analysis/cognito_credentials
"""

import requests
import sys

from scs_analysis.cmd.cmd_aws_organisations import CmdAWSOrganisations

from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials

from scs_core.aws.security.organisation import Organisation
from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.comms.stdio import StdIO
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    credentials = None
    authentication = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdAWSOrganisations()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('aws_organisations', verbose=cmd.verbose)
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
            report = manager.find_organisations(authentication.id_token)

        if cmd.retrieve:
            report = manager.get_organisation_by_label(authentication.id_token, cmd.retrieve)

        if cmd.create:
            org = Organisation(0, cmd.label, cmd.long_name, cmd.url, cmd.owner)
            report = manager.insert_organisation(authentication.id_token, org)

        if cmd.update:
            # find...
            org = manager.get_organisation_by_label(authentication.id_token, cmd.update)

            if org is None:
                logger.error("no organisation found for label: '%s'." % cmd.update)
                exit(1)

            # update...
            label = org.label if cmd.label is None else cmd.label
            long_name = org.long_name if cmd.long_name is None else cmd.long_name
            url = org.url if cmd.url is None else cmd.url
            owner = org.owner if cmd.owner is None else cmd.owner

            report = Organisation(org.org_id, label, long_name, url, owner)
            manager.update_organisation(authentication.id_token, report)

        if cmd.delete:
            # find...
            org = manager.get_organisation_by_label(authentication.id_token, cmd.update)

            if org is None:
                logger.error("no organisation found for label: '%s'" % cmd.delete)
                exit(1)

            # check...
            response = StdIO.prompt('Are you sure (Y/n)?')
            if response != 'Y':
                exit(0)

            # delete...
            manager.delete_organisation(authentication.id_token, cmd.delete)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
