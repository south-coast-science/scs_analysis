#!/usr/bin/env python3

"""
Created on 8 Aug 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
Usage statistics are continuously collected for each web API by endpoint, date and user. The client_traffic utility is
used to query these statistics. Compulsory query fields are:

* -p PERIOD - should be in the form YYYY, YYYY-MM, or YYYY-MM-DD
* -u or -o CLIENT_1 [.. CLIENT_N] - specifies one or more email addresses, or one or more organisation labels

Optional query fields are:

* -e ENDPOINT - if specified, statistics for the given endpoint are reported, otherwise, all endpoints are reported

Other parameters are:

* --separate - (only permitted when specifying a single organisation) the organisation is broken down by individual
user members
* --aggregate - (only relevant when specifying a year or month period) statistics are aggregated to totals for the
period

Statistics are available only for the clients(s) that are visible to the user. Only organisation admins may view
statistics for whole organisations. Only superusers can view the statistics for all users.

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
Usage: client_traffic.py [-c CREDENTIALS] -e ENDPOINT [{ -u | -o [-s] }] -p PERIOD [-a] [-i INDENT] [-v]
[CLIENT_1...CLIENT_N]

EXAMPLES
client_traffic.py -c super -e test1 -o Ricardo -p 2023-08-22

client_traffic.py -v -c super -e TopicHistory -p 2024 -u production@southcoastscience.com | node.py -s | \
csv_writer.py -v traffic.csv

DOCUMENT EXAMPLE
[
    {
        "endpoint": "TopicHistory",
        "client": "production@southcoastscience.com",
        "period": "2024",
        "queries": 855,
        "invocations": 855,
        "characters": 266633895
    }
]

SEE ALSO
scs_analysis/cognito_user_credentials
"""

import sys

from scs_analysis.cmd.cmd_client_traffic import CmdClientTraffic

from scs_core.aws.client_traffic.client_traffic import ClientTrafficLocus
from scs_core.aws.client_traffic.client_traffic_finder import ClientTrafficFinder
from scs_core.aws.client_traffic.client_traffic_intercourse import ClientTrafficRequest

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user_finder import CognitoUserFinder
from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.client.http_exception import HTTPException

from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    clients = []
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

        if not cmd.organisation and not cmd.user and not cmd.endpoint:
            logger.error("an endpoint must be specified if no user or organisation is specified.")
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        user_finder = CognitoUserFinder()
        organisation_finder = OrganisationManager()
        traffic_finder = ClientTrafficFinder()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.user:
            for client in cmd.clients:
                user = user_finder.get_by_email(auth.id_token, client)

                # if user is None:
                #     logger.error("the user '%s' could not be found." % client)
                #     exit(2)

                email = client if user is None else user.email      # include API keys

                clients.append(email)

        elif cmd.organisation:
            for client in cmd.clients:
                organisation = organisation_finder.get_organisation_by_label(auth.id_token, client)

                if organisation is None:
                    logger.error("the organisation '%s' could not be found." % client)
                    exit(2)

                clients.append(organisation.label)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        request = ClientTrafficRequest(cmd.endpoint, clients, cmd.period, cmd.aggregate)

        if cmd.organisation:
            if cmd.separate:
                report = traffic_finder.find_for_organisations_users(auth.id_token, request)
            else:
                report = traffic_finder.find_for_organisations(auth.id_token, request)

        elif cmd.user:
            report = traffic_finder.find_for_users(auth.id_token, request)

        else:
            report = traffic_finder.find_for_endpoint(auth.id_token, request)

        report = sorted(report)


        # ------------------------------------------------------------------------------------------------------------
        # end...

        # report...
        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))
            logger.info('reports: %s' % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
