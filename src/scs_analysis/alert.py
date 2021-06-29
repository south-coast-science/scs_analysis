#!/usr/bin/env python3

"""
Created on 29 Jun 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The alert utility is used to

SYNOPSIS
alert.py  { -f TOPIC | -r ID | -c | -u ID | -d ID } [-o TOPIC] [-e FIELD] [-l LOWER] [-p UPPER] [-n { 1 | 0 }]
[-a AGGREGATION] [-t INTERVAL] [-s { 1 | 0 }] [-m EMAIL_ADDR] [-x EMAIL_ADDR] [-i INDENT] [-v]

EXAMPLES
alert.py -c -o my/topic -e my.field -l 10 -a 10:00 -v

DOCUMENT EXAMPLE

SEE ALSO
scs_analysis/alert_status
scs_analysis/monitor_auth
"""

import requests
import sys

from scs_analysis.cmd.cmd_alert import CmdAlert

from scs_core.aws.client.monitor_auth import MonitorAuth
from scs_core.aws.data.alert import Alert
from scs_core.aws.manager.alert_finder import AlertFinder

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    auth = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdAlert()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('alert', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not MonitorAuth.exists(Host):
            logger.error('access key not available')
            exit(1)

        try:
            auth = MonitorAuth.load(Host, encryption_key=MonitorAuth.password_from_user())
        except (KeyError, ValueError):
            logger.error('incorrect password')
            exit(1)

        finder = AlertFinder(requests, auth)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            response = finder.find(cmd.find_topic, cmd.field, auth.email_address)
            report = sorted(response.alerts)

        if cmd.retrieve:
            response = finder.retrieve(cmd.retrieve_id, auth.email_address)
            report = response.alerts[0] if response.alerts else None

        if cmd.create:
            if not cmd.is_complete():
                logger.error("minimum parameters are topic, path, a threshold, and an aggregation period.")
                exit(2)

            alert = Alert(None, cmd.topic, cmd.field, cmd.lower_threshold, cmd.upper_threshold, cmd.alert_on_none,
                          cmd.aggregation_period, cmd.test_interval, auth.email_address, [], cmd.suspended)

            if not alert.has_valid_thresholds():
                logger.error("threshold values are invalid.")
                exit(2)

            # TODO: do create (and retrieve)

            report = alert

        if cmd.update:
            if cmd.topic is not None or cmd.field is not None:
                logger.error("topic and field may not be changed.")
                exit(2)

            response = finder.retrieve(cmd.retrieve_id, auth.email_address)
            alert = response.alerts[0] if response.alerts else None

            if alert is None:
                logger.error("no alert found with ID %s." % cmd.update_id)
                exit(1)

            lower_threshold = alert.lower_threshold if cmd.lower_threshold is None else cmd.lower_threshold
            upper_threshold = alert.upper_threshold if cmd.upper_threshold is None else cmd.upper_threshold
            alert_on_none = alert.alert_on_none if cmd.alert_on_none is None else bool(cmd.alert_on_none)
            aggregation_period = alert.aggregation_period if cmd.aggregation_period is None else cmd.aggregation_period
            test_interval = alert.test_interval if cmd.test_interval is None else cmd.test_interval
            suspended = alert.suspended if cmd.suspended is None else bool(cmd.suspended)

            if cmd.add_cc is not None:
                if not Datum.is_email_address(cmd.add_cc):
                    logger.error("the email address '%s' is not valid." % cmd.add_cc)
                    exit(1)

                alert.append_to_cc_list(cmd.add_cc)

            if cmd.remove_cc is not None:
                alert.remove_from_cc_list(cmd.remove_cc)

            alert = Alert(cmd.update_id, cmd.topic, cmd.field, lower_threshold, upper_threshold, alert_on_none,
                          aggregation_period, test_interval, auth.email_address, alert.cc_list, suspended)

            if not alert.has_valid_thresholds():
                logger.error("threshold values are invalid.")
                exit(2)

            # TODO: do update

            report = alert

            if cmd.delete:
                response = finder.retrieve(cmd.retrieve_id, auth.email_address)
                alert = response.alerts[0] if response.alerts else None

                if alert is None:
                    logger.error("no alert found with ID %s." % cmd.update_id)
                    exit(1)

            # TODO: do delete

        # report...
        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        now = LocalizedDatetime.now().utc().as_iso8601()
        logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
        exit(1)
