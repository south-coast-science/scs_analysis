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
alert.py -c -o south-coast-science-dev/development/loc/1/gases -e val.H2S.cn -n1 -a 1:00:00 -i4 -v

DOCUMENT EXAMPLE
{"id": 123, "topic": "my/topic", "field": "my.field", "lower-threshold": 10.0, "upper-threshold": 100.0,
"alert-on-none": true, "aggregation-period": "00-01:00:00", "test-interval": "00-00:05:00",
"creator-email-address": "bruno.beloff@southcoastscience.com", "cc-list": ["bbeloff@me.com"], "suspended": false}

SEE ALSO
scs_analysis/alert_status
scs_analysis/monitor_auth
"""

import json

import requests
import sys

from scs_analysis.cmd.cmd_alert import CmdAlert

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.client.monitor_auth import MonitorAuth

from scs_core.aws.data.alert import AlertSpecification

from scs_core.aws.manager.alert_finder import AlertFinder
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.datum import Datum
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.data.str import Str

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    auth = None
    response = None
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

        # MonitorAuth...
        if not MonitorAuth.exists(Host):
            logger.error('access key not available')
            exit(1)

        try:
            auth = MonitorAuth.load(Host, encryption_key=MonitorAuth.password_from_user())
        except (KeyError, ValueError):
            logger.error('incorrect password')
            exit(1)

        finder = AlertFinder(requests, auth)
        logger.info(finder)

        # APIAuth...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            logger.error("APIAuth not available.")
            exit(1)

        logger.info(api_auth)

        # byline manager...
        byline_manager = BylineManager(api_auth)
        logger.info(byline_manager)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            response = finder.find(cmd.find_topic, cmd.field, auth.email_address)
            report = sorted(response.alerts)

        if cmd.retrieve:
            response = finder.retrieve(cmd.retrieve_id, auth.email_address)
            report = response.alerts[0] if response.alerts else None

        if cmd.create:
            # validate...
            if not cmd.is_complete():
                logger.error("minimum parameters are topic, path, a threshold, and an aggregation period.")
                exit(2)

            byline = byline_manager.find_latest_byline_for_topic(cmd.topic)

            if byline is None or cmd.topic != byline.topic:
                logger.error("the topic '%s' is not available." % cmd.topic)
                exit(2)

            message = PathDict(json.loads(byline.message))

            if not message.has_path(cmd.field):
                paths = Str.collection(message.paths())
                logger.error("the field '%s' is not available. Available fields are: %s" % (cmd.field, paths))
                exit(2)

            # create...
            alert = AlertSpecification(None, cmd.topic, cmd.field, cmd.lower_threshold, cmd.upper_threshold,
                                       cmd.alert_on_none, cmd.aggregation_period, cmd.test_interval, auth.email_address,
                                       [], cmd.suspended)

            if not alert.has_valid_thresholds():
                logger.error("threshold values are invalid.")
                exit(2)

            if not alert.has_valid_aggregation_period():
                logger.error("the aggregation period is invalid.")
                exit(2)

            # TODO: do create (and retrieve)

            report = alert

        if cmd.update:
            # validate...
            if cmd.topic is not None or cmd.field is not None:
                logger.error("topic and field may not be changed.")
                exit(2)

            response = finder.retrieve(cmd.retrieve_id, auth.email_address)
            alert = response.alerts[0] if response.alerts else None

            if alert is None:
                logger.error("no alert found with ID %s." % cmd.update_id)
                exit(2)

            if auth.email_address != alert.creator_email_address:
                logger.error("you do not have permission to update this alert.")
                exit(2)

            # update...
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

            alert = AlertSpecification(alert.update_id, alert.topic, alert.field, lower_threshold, upper_threshold,
                                       alert_on_none, aggregation_period, test_interval, alert.creator_email_address,
                                       alert.cc_list, suspended)

            if not alert.has_valid_thresholds():
                logger.error("threshold values are invalid.")
                exit(2)

            if not alert.has_valid_aggregation_period():
                logger.error("the aggregation period is invalid.")
                exit(2)

            # TODO: do update

            report = alert

            if cmd.delete:
                response = finder.retrieve(cmd.retrieve_id, auth.email_address)
                alert = response.alerts[0] if response.alerts else None

                if alert is None:
                    logger.error("no alert found with ID %s." % cmd.update_id)
                    exit(2)

            # TODO: do delete

        # report...
        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.find:
            logger.info('retrieved: %s' % len(response.items))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        now = LocalizedDatetime.now().utc().as_iso8601()
        logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
        exit(1)
