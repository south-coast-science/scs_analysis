#!/usr/bin/env python3

"""
Created on 8 Aug 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The client_traffic utility is used to

SYNOPSIS
client_traffic.py [-c CREDENTIALS] [-e ENDPOINT] { -u EMAIL | -l ORG_LABEL [-s] } -p PERIOD [-a] [-i INDENT] [-v]

EXAMPLES

DOCUMENT EXAMPLE

SEE ALSO
scs_analysis/cognito_user_credentials
"""

import sys

from scs_analysis.cmd.cmd_client_traffic import CmdClientTraffic

from scs_core.aws.security.client_traffic import ClientTrafficLocus
from scs_core.aws.security.client_traffic_finder import ClientTrafficFinder, ClientTrafficRequest

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user_finder import CognitoUserFinder

from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.client.http_exception import HTTPException, HTTPNotFoundException

from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    response = None
    report = None

    # ------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdClientTraffic()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('client_traffic', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
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
        # validation...

        if not ClientTrafficLocus.is_valid_period(cmd.period):
            logger.error("the period '%s' is not valid." % cmd.period)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        user_finder = CognitoUserFinder()
        organisation_finder = OrganisationManager()
        traffic_finder = ClientTrafficFinder()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.user:
            user = user_finder.get_by_email(auth.id_token, cmd.user)

            if user is None:
                logger.error("the user '%s' could not be found." % cmd.user)
                exit(2)

            print("user: %s" % user)

        else:
            organisation = organisation_finder.get_organisation_by_label(auth.id_token, cmd.organisation)

            if organisation is None:
                logger.error("the organisation '%s' could not be found." % cmd.organisation)
                exit(2)

            print("organisation: %s" % organisation)

            org_users = organisation_finder.find_users_by_organisation(auth.id_token, organisation.org_id)

            usernames = [org_user.username for org_user in org_users]
            print("usernames: %s" % usernames)

            users = user_finder.find_by_usernames(auth.id_token, usernames)

            # if cmd.separate:
            #     users = organisation_finder.find_users_by_organisation(auth.id_token, organisation.org_id)

            for user in users:
                print("user: %s" % user)

                # TODO: exclude bruno.beloff, etc.


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # request = ClientTrafficRequest(cmd.endpoint, clients, cmd.period, cmd.aggregate)
        #
        # if cmd.organisation and not cmd.separate:
        #     response = traffic_finder.find_for_organisation(auth.id_token, request)
        # else:
        #     response = traffic_finder.find_for_user(auth.id_token, request)


        # ------------------------------------------------------------------------------------------------------------
        # end...

        # report...
        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))


    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)
