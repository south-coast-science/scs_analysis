#!/usr/bin/env python3

"""
Created on 29 Jun 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The alert_status utility is used to report on the history of alerts generated by a specific alert specification.
Alert causes are:

* L - Below lower threshold
* U - Above upper threshold
* N - Null value
* OK - data has returned within bounds

SYNOPSIS
alert_status.py [-c CREDENTIALS] { -F { -l | -d [-a CAUSE] } | -D } [-i INDENT] [-v] ID

EXAMPLES
alert_status.py -vi4 -c bruno -Fl 87

alert_status.py -v -c bruno -Fd 107 | node.py -s | csv_writer.py

DOCUMENT EXAMPLE
{"id": 88, "rec": "2023-06-29T09:48:42Z", "cause": "NV", "val": null}

SEE ALSO
scs_analysis/alert
scs_analysis/cognito_user_credentials
"""

import sys

from scs_analysis.cmd.cmd_alert_status import CmdAlertStatus

from scs_core.aws.monitor.alert.alert_status_manager import AlertStatusManager

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

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

    cmd = CmdAlertStatus()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('alert_status', verbose=cmd.verbose)
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
        # resources...

        status_manager = AlertStatusManager()


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        try:
            int(cmd.id)
        except (TypeError, ValueError):
            logger.error('the ID must be an integer.')
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            if cmd.latest:
                response = status_manager.find(auth.id_token, cmd.id, None, cmd.response_mode())
                report = response.alert_statuses[0] if response.alert_statuses else None

            if cmd.history:
                response = status_manager.find(auth.id_token, cmd.id, cmd.cause, cmd.response_mode())
                report = sorted(response.alert_statuses)

        if cmd.delete:
            status_manager.delete(auth.id_token, cmd.id)
            logger.warning("status history has been queued for deletion.")


        # ------------------------------------------------------------------------------------------------------------
        # end...

        # report...
        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.history:
            logger.info('retrieved: %s' % len(response.alert_statuses))


    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPNotFoundException:
        logger.error("no alert found with ID %s." % cmd.id)
        exit(2)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
