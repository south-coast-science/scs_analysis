#!/usr/bin/env python3

"""
Created on 29 Jun 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The alert utility is used to create, update, delete or find alert specifications.

Alerts take the form of emails. These are sent when a parameter falls below or above specified bounds, or when the
value is null (a null value is being reported, or no reports are available). The alert specification sets these bounds,
together with the aggregation period (usually in minutes). The minimum period is one minute.

Important note: when an alert is triggered, only one email is sent to each of the specified recipients. No further
email is sent until the parameter has returned within bounds and then, subsequently, exceeds the bounds. The end of an
out-of-bound event is logged in the alert status history. A history of out-of-bounds events for each alert
specification can be found using the alert_status utility.

In --find mode, results can be filtered by description, topic, field or email address.
Finder matches are exact.

SYNOPSIS
alert.py { -z | [-c CREDENTIALS]  { -F | -R ID | -C | -U ID | -D ID } [-d DESCRIPTION] [-p TOPIC] [-f FIELD]
[-l LOWER] [-u UPPER] [-n { 0 | 1 }] [{ -r INTERVAL UNITS TIMEZONE | -t START END TIMEZONE }] [-j { 0 | 1 }]
[-s { 0 | 1 }] [-i INDENT] [-v] [-e EMAIL_ADDR] [-g EMAIL_ADDR_1 .. EMAIL_ADDR_N]}

EXAMPLES
alert.py -vi4 -c super -C -d be2-3-nightime-test -p south-coast-science-dev/development/loc/1/climate -f val.tmp \
-u 10 -n 1 -t 16:00 8:00 Europe/London -e bruno.beloff@southcoastscience.com -g jade.page@southcoastscience.com

DOCUMENT EXAMPLE (recurring)
{"id": null, "description": "my description", "topic": "my/topic",
"field": "my.field", "lower-threshold": null,  "upper-threshold": 100.0, "alert-on-none": true,
"aggregation-period": {"type": "recurring", "interval": 1, "units": "D", "timezone": "Europe/London"},
"test-interval": {"type": "recurring", "interval": 1, "units": "M"}, "json-message": true,
"creator-email-address": "bruno.beloff@southcoastscience.com", "to": "bruno.beloff@southcoastscience.com",
"cc-list": ["bbeloff@me.com", "hhopton@me.com"], "suspended": false}

DOCUMENT EXAMPLE (diurnal)
{"id": 107, "description": "be2-3-nightime-test", "topic": "south-coast-science-dev/development/loc/1/climate",
"field": "val.tmp", "lower-threshold": null, "upper-threshold": 10.0, "alert-on-none": true,
"aggregation-period": {"type": "diurnal", "start": "16:00:00", "end": "08:00:00", "timezone": "Europe/London"},
"test-interval": null, "json-message": false, "creator-email-address": "production@southcoastscience.com",
"to": "bruno.beloff@southcoastscience.com", "cc-list": ["jade.page@southcoastscience.com"], "suspended": false}

SEE ALSO
scs_analysis/alert_status
scs_analysis/cognito_user_credentials

BUGS
The test-interval field is not currently in use, and is ignored.
"""

import json
import requests
import sys

from scs_analysis.cmd.cmd_alert import CmdAlert

from scs_core.aws.data.alert import AlertSpecification

from scs_core.aws.manager.alert_specification_manager import AlertSpecificationManager
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException, HTTPNotFoundException

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.data.str import Str

from scs_core.location.timezone import Timezone

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    credentials = None
    auth = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdAlert()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('alert', verbose=cmd.verbose)        # level=logging.DEBUG
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        if not cmd.list:
            credentials = CognitoClientCredentials.load_for_user(Host, name=cmd.credentials_name)

            if not credentials:
                exit(1)

            gatekeeper = CognitoLoginManager(requests)
            auth = gatekeeper.user_login(credentials)

            if not auth.is_ok():
                logger.error("login: %s" % auth.authentication_status.description)
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        byline_manager = BylineManager(requests)
        specification_manager = AlertSpecificationManager(requests)


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        try:
            if cmd.id is not None:
                int(cmd.id)
        except (TypeError, ValueError):
            logger.error('the ID must be an integer.')
            exit(2)

        if cmd.email is not None and not Datum.is_email_address(cmd.email):
            logger.error("the email address '%s' is not valid." % cmd.email)
            exit(2)

        if cmd.cc:
            for email in cmd.cc_list:
                if email is not None and not Datum.is_email_address(email):
                    logger.error("the email address '%s' is not valid." % email)
                    exit(2)

        if not cmd.is_valid_start_time():
            logger.error("the start time is invalid.")
            exit(2)

        if not cmd.is_valid_end_time():
            logger.error("the end time is invalid.")
            exit(2)

        if not cmd.is_valid_timezone():
            logger.error("the timezone is invalid.")
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.list:
            for zone in Timezone.zones():
                print(zone, file=sys.stderr)
            exit(0)

        if cmd.find:
            response = specification_manager.find(auth.id_token, cmd.description, cmd.topic, cmd.field, None)
            filtered = [alert for alert in response.alerts if cmd.email in alert] if cmd.email else response.alerts

            report = sorted(filtered)

        if cmd.retrieve:
            report = specification_manager.retrieve(auth.id_token, cmd.id)

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
            to = credentials.email if cmd.email is None else cmd.email
            cc = cmd.cc_list if cmd.cc else {}

            alert = AlertSpecification(None, cmd.description, cmd.topic, cmd.field, cmd.lower_threshold,
                                       cmd.upper_threshold, cmd.alert_on_none, cmd.aggregation_period,
                                       None, bool(cmd.json_message), None, to, cc, bool(cmd.suspended))

            if not alert.has_valid_thresholds():
                logger.error("threshold values are invalid.")
                exit(2)

            if not alert.has_valid_aggregation_period():
                logger.error("the aggregation period is invalid.")
                exit(2)

            report = specification_manager.create(auth.id_token, alert)

        if cmd.update:
            # validate...
            if cmd.topic is not None or cmd.field is not None:
                logger.error("topic and field may not be changed.")
                exit(2)

            alert = specification_manager.retrieve(auth.id_token, cmd.id)

            if alert is None:
                logger.error("no alert found with ID %s." % cmd.id)
                exit(2)

            # update...
            description = alert.description if not cmd.description else cmd.description
            lower_threshold = alert.lower_threshold if cmd.lower_threshold is None else cmd.lower_threshold
            upper_threshold = alert.upper_threshold if cmd.upper_threshold is None else cmd.upper_threshold
            alert_on_none = alert.alert_on_none if cmd.alert_on_none is None else bool(cmd.alert_on_none)
            aggregation_period = alert.aggregation_period if cmd.aggregation_period is None else cmd.aggregation_period
            json_message = alert.json_message if cmd.json_message is None else bool(cmd.json_message)
            suspended = alert.suspended if cmd.suspended is None else bool(cmd.suspended)
            to = alert.to if cmd.email is None else cmd.email
            cc = cmd.cc_list if cmd.cc else alert.cc_list

            updated = AlertSpecification(alert.id, description, alert.topic, alert.field, lower_threshold,
                                         upper_threshold, alert_on_none, aggregation_period, None,
                                         json_message, alert.creator_email_address, to, cc, suspended)

            if not updated.has_valid_thresholds():
                logger.error("threshold values are invalid.")
                exit(2)

            if not updated.has_valid_aggregation_period():
                logger.error("the aggregation period is invalid.")
                exit(2)

            report = specification_manager.update(auth.id_token, updated)

        if cmd.delete:
            try:
                specification_manager.delete(auth.id_token, cmd.id)
            except HTTPNotFoundException:
                logger.error("no alert found with ID %s." % cmd.id)


        # ------------------------------------------------------------------------------------------------------------
        # end...

        # report...
        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.find:
            logger.info('retrieved: %s' % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)
