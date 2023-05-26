#!/usr/bin/env python3

"""
Created on 29 Jun 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The alert utility is used to create, update, delete and find alert specifications.

Alerts take the form of emails, sent when a parameter falls below or above specified bounds, or when the value is null
(a null value is being reported, or no reports are available). The alert specification sets these bounds, together with
the aggregation period (usually in minutes). The minimum period is one minute.

In --find mode, results can be filtered by topic, field or creator email address.

SYNOPSIS
alert.py [-c CREDENTIALS]  { -F | -R ID | -C | -U ID | -D ID } [-p TOPIC] [-f FIELD] [-l LOWER] [-u UPPER]
[-n { 1 | 0 }] [-a INTERVAL UNITS] [-t INTERVAL] [-s { 1 | 0 }] [-e EMAIL_ADDR] [-i INDENT] [-v]

EXAMPLES


DOCUMENT EXAMPLE
{"id": 77, "topic": "south-coast-science-dev/development/loc/1/gases", "field": "val.CO.cnc", "lower-threshold": null,
"upper-threshold": 1000.0, "alert-on-none": true, "aggregation-period": {"interval": 1, "units": "M"},
"test-interval": null, "creator-email-address": "authorization@southcoastscience.com",
"to": "someone@me.com", "cc-list": [], "suspended": false}

SEE ALSO
scs_analysis/alert_status
scs_analysis/monitor_auth

BUGS
* The --test-interval flag is not currently in use, and is ignored.
* Email CC addresses cannot be added or removed.
"""

import json
import requests
import sys

from scs_analysis.cmd.cmd_alert import CmdAlert

from scs_core.aws.client.api_auth import APIAuth

from scs_core.aws.data.alert import AlertSpecification

from scs_core.aws.manager.alert_specification_manager import AlertSpecificationManager
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.data.str import Str

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    response = None
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

        credentials = CognitoClientCredentials.load_for_user(Host, name=cmd.credentials_name)

        if not credentials:
            exit(1)

        gatekeeper = CognitoLoginManager(requests)
        auth = gatekeeper.user_login(credentials)

        if not auth.is_ok():
            logger.error("login: %s" % auth.authentication_status.description)
            exit(1)

        # APIAuth (for BylineManager)...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            logger.error("APIAuth is not available")
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        alert_manager = AlertSpecificationManager(requests)
        byline_manager = BylineManager(requests)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            # creator_filter = auth.email_address if cmd.creator is None else cmd.creator     # TODO: remove
            response = alert_manager.find(auth.id_token, cmd.topic, cmd.field, None)
            report = sorted(response.alerts)

        if cmd.retrieve:
            report = alert_manager.retrieve(auth.id_token, cmd.retrieve_id)

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
            to = auth.email_address if cmd.to is None else cmd.to

            alert = AlertSpecification(None, cmd.topic, cmd.field, cmd.lower_threshold, cmd.upper_threshold,
                                       cmd.alert_on_none, cmd.aggregation_period, cmd.test_interval, None,
                                       to, [], cmd.suspended)

            if not alert.has_valid_thresholds():
                logger.error("threshold values are invalid.")
                exit(2)

            if not alert.has_valid_aggregation_period():
                logger.error("the aggregation period is invalid.")
                exit(2)

            if not alert.is_valid():
                logger.error("the alert is invalid.")
                exit(2)

            report = alert_manager.create(auth.id_token, alert)

        if cmd.update:
            # validate...
            if cmd.topic is not None or cmd.field is not None:
                logger.error("topic and field may not be changed.")
                exit(2)

            alert = alert_manager.retrieve(auth.id_token, cmd.update_id)

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
            to = alert.to if cmd.to is None else cmd.to

            updated = AlertSpecification(alert.id, alert.topic, alert.field, lower_threshold, upper_threshold,
                                         alert_on_none, aggregation_period, test_interval, alert.creator_email_address,
                                         to, alert.cc_list, suspended)

            if not updated.has_valid_thresholds():
                logger.error("threshold values are invalid.")
                exit(2)

            if not updated.has_valid_aggregation_period():
                logger.error("the aggregation period is invalid.")
                exit(2)

            report = alert_manager.update(auth.id_token, updated)

        if cmd.delete:
            alert = alert_manager.retrieve(auth.id_token, cmd.delete_id)

            if alert is None:
                logger.error("no alert found with ID %s." % cmd.delete_id)
                exit(2)

            alert_manager.delete(auth.id_token, cmd.delete_id)


        # ------------------------------------------------------------------------------------------------------------
        # end...

        # report...
        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.find:
            logger.info('retrieved: %s' % len(response.alerts))


        # ------------------------------------------------------------------------------------------------------------
        # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    # except HTTPException as ex:
    #     now = LocalizedDatetime.now().utc().as_iso8601()
    #     logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
    #     exit(1)
