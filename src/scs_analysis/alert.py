#!/usr/bin/env python3

"""
Created on 29 Jun 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The alert utility is used to create, update, delete or find alert specifications.

Alerts take the form of emails. These are sent when a parameter falls below or above specified bounds, or when the
value is null (a null value is being reported, or no reports are available). The alert specification sets these bounds,
together with the aggregation period. One of two types of period may be specified:

* Recurring - a period of a given number of minutes, hours or days. Recurring periods are sampled back-to back.
* Diurnal - a daily period with given start time and end times. Diurnal periods are sampled immediately after the end
time.

In --find mode, results can be filtered by description, topic, field or email address. Finder matches are exact.

When doing an update, the cc list (-g flag) may be preceeded with:

* A - add the following email address(es)
* R - remove the following email address(es)

If neither indicator is used, then the specified email address(es) replace the current ones.

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
alert.py { -z | [-c CREDENTIALS]  { -F | -R ID | -C | -U ID | -D ID } [-d DESCRIPTION] [-p TOPIC] [-f FIELD]
[-l LOWER] [-u UPPER] [-n { 0 | 1 }] [{ -r INTERVAL UNITS TIMEZONE | -t START END TIMEZONE }]
[-a { 0 | 1 }] [-s { 0 | 1 }] [-i INDENT] [-v] [-e EMAIL_ADDR] [-b { A | R } EMAIL_ADDR [-j]] }

EXAMPLES
alert.py -vi4 -c super -C -d be2-3-nightime-test -p south-coast-science-dev/development/loc/1/climate -f val.tmp \
-u 10 -n 1 -t 16:00 8:00 Europe/London -e bruno.beloff@southcoastscience.com -g jade.page@southcoastscience.com

DOCUMENT EXAMPLE (recurring)
{"id": 85, "description": "test", "topic": "south-coast-science-demo/brighton-urban/loc/1/particulates",
"field": "exg.val.pm2p5", "lower-threshold": null, "upper-threshold": 20.0, "alert-on-none": false,
"aggregation-period": {"type": "recurring", "interval": 1, "units": "M", "timezone": "Europe/London"},
"contiguous-alerts": false, "json-message": false, "creator-email-address": "bruno.beloff@southcoastscience.com",
"to": "bruno.beloff@southcoastscience.com", "cc-list": [], "suspended": false}

DOCUMENT EXAMPLE (diurnal)
{"id": 107, "description": "be2-3-nightime-test", "topic": "south-coast-science-dev/development/loc/1/climate",
"field": "val.tmp", "lower-threshold": null, "upper-threshold": 10.0, "alert-on-none": false,
"aggregation-period": {"type": "diurnal", "start": "20:00:00", "end": "09:50:00", "timezone": "Europe/London"},
"contiguous-alerts": true, "json-message": false, "creator-email-address": "production@southcoastscience.com",
"to": "bruno.beloff@southcoastscience.com", "cc-list": ["jade.page@southcoastscience.com"], "suspended": false}

SEE ALSO
scs_analysis/alert_status
scs_analysis/cognito_user_credentials

BUGS
The test-interval field is not currently in use, and is ignored.
"""

import json
import sys

from scs_analysis.cmd.cmd_alert import CmdAlert

from scs_core.aws.monitor.alert.alert import AlertSpecification

from scs_core.aws.monitor.alert.alert_specification_manager import AlertSpecificationManager
from scs_core.aws.manager.byline.byline_finder import BylineFinder

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException, HTTPNotFoundException

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.data.str import Str

from scs_core.email.email import EmailRecipient

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

        Logging.config('alert', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        if not cmd.list:
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

        byline_finder = BylineFinder()
        specification_manager = AlertSpecificationManager()


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

        if cmd.bcc:
            if not Datum.is_email_address(cmd.bcc_email):
                logger.error("the email address '%s' is not valid." % cmd.bcc_email)
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
            # validation...
            if not cmd.is_complete():
                logger.error("minimum parameters are topic, path, a threshold, and an aggregation period.")
                exit(2)

            byline = byline_finder.find_latest_byline_for_topic(auth.id_token, cmd.topic)

            if byline is None or cmd.topic != byline.topic:
                logger.error("the topic '%s' is not available." % cmd.topic)
                exit(2)

            message = PathDict(json.loads(byline.message))

            if not message.has_path(cmd.field):
                paths = Str.collection(message.paths())
                logger.error("the field '%s' is not available. Available fields are: %s." % (cmd.field, paths))
                exit(2)

            # create...
            contiguous_alerts = True if cmd.contiguous_alerts is None else bool(cmd.contiguous_alerts)
            to_email = credentials.email if cmd.email is None else cmd.email
            to = EmailRecipient(to_email, cmd.json_message)

            bcc_dict = {}

            alert = AlertSpecification(None, cmd.description, cmd.topic, cmd.field, cmd.lower_threshold,
                                       cmd.upper_threshold, cmd.alert_on_none, cmd.aggregation_period,
                                       None, contiguous_alerts, None, to, bcc_dict, bool(cmd.suspended))

            if not alert.has_valid_thresholds():
                logger.error("threshold values are invalid.")
                exit(2)

            if not alert.has_valid_aggregation_period():
                logger.error("the aggregation period is invalid.")
                exit(2)

            report = specification_manager.create(auth.id_token, alert)

        if cmd.update:
            #  validation...
            if cmd.topic is not None:
                logger.error("topic may not be changed.")
                exit(2)

            alert = specification_manager.retrieve(auth.id_token, cmd.id)

            if alert is None:
                logger.error("no alert found with ID %s." % cmd.id)
                exit(2)

            # update...
            field = alert.field if not cmd.field else cmd.field
            description = alert.description if not cmd.description else cmd.description
            lower_threshold = alert.lower_threshold if cmd.lower_threshold is None else cmd.lower_threshold
            upper_threshold = alert.upper_threshold if cmd.upper_threshold is None else cmd.upper_threshold
            alert_on_none = alert.alert_on_none if cmd.alert_on_none is None else bool(cmd.alert_on_none)
            aggregation_period = alert.aggregation_period if cmd.aggregation_period is None else cmd.aggregation_period
            contiguous_alerts = alert.contiguous_alerts if cmd.contiguous_alerts is None else cmd.contiguous_alerts
            suspended = alert.suspended if cmd.suspended is None else bool(cmd.suspended)
            to_email = alert.to.email_address if cmd.email is None else cmd.email
            to = EmailRecipient(to_email, cmd.json_message)

            bcc_dict = cmd.updated_bcc_dict(alert.bcc_dict)

            updated = AlertSpecification(alert.id, description, alert.topic, field, lower_threshold, upper_threshold,
                                         alert_on_none, aggregation_period, None, contiguous_alerts,
                                         alert.creator_email_address, to, bcc_dict, suspended)

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

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
