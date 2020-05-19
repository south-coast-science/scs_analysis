#!/usr/bin/env python3

"""
Created on 6 Nov 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_topic_history utility is used to retrieve stored data from the South Coast Science / AWS historic data
retrieval system. Data can be retrieved by start or start + end localised date / times, or by a days / hours / minutes
timedelta back in time from now. A further "latest" mode returns the most recent document, or none if the topic has
never received a publication.

The --rec-only flag causes only the rec fields on the documents to be returned. This results in much faster data
retrieval, and is useful if sampling continuity is being tested.

Note that no check is made for the existence of the topic - if the topic does not exist, then no error is raised and
no data is returned.

Equivalent to cURL:
curl "https://aws.southcoastscience.com/topicMessages?topic=south-coast-science-dev/production-test/loc/1/gases
&startTime=2018-12-13T07:03:59.712Z&endTime=2018-12-13T15:10:59.712Z"

SYNOPSIS
aws_topic_history.py { -l | -t { [[DD-]HH:]MM[:SS] | :SS } | -s START [-e END] } [-r] [-w] [-v] TOPIC

EXAMPLES
aws_topic_history.py south-coast-science-dev/production-test/loc/1/gases -t 1 -v -w

DOCUMENT EXAMPLE - OUTPUT
{"device": "scs-bbe-401", "topic": "south-coast-science-demo/brighton/loc/1/climate", "upload": "2019-01-11T12:15:36Z",
"payload": {"val": {"hmd": 68.4, "tmp": 12.3}, "rec": "2019-01-11T12:15:36Z", "tag": "scs-bgx-401"}}

{"val": {"hmd": 68.4, "tmp": 12.3}, "rec": "2019-01-11T12:15:36Z", "tag": "scs-bgx-401"}

FILES
~/SCS/aws/aws_api_auth.json

SEE ALSO
scs_analysis/aws_api_auth
scs_analysis/localised_datetime

RESOURCES
https://github.com/curl/curl
"""

import sys

from scs_analysis.cmd.cmd_aws_topic_history import CmdAWSTopicHistory
from scs_analysis.handler.aws_topic_history_reporter import AWSTopicHistoryReporter

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.manager.byline_manager import BylineManager
from scs_core.aws.manager.lambda_message_manager import MessageManager

from scs_core.client.http_client import HTTPClient
from scs_core.client.network_unavailable_exception import NetworkUnavailableException

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSTopicHistory()

    if not cmd.is_valid_start():
        print("aws_topic_history: invalid format for start datetime.", file=sys.stderr)
        exit(2)

    if not cmd.is_valid_end():
        print("aws_topic_history: invalid format for end datetime.", file=sys.stderr)
        exit(2)

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)


    if cmd.verbose:
        print("aws_topic_history: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # APIAuth...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            print("aws_topic_history: APIAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("aws_topic_history: %s" % api_auth, file=sys.stderr)

        # reporter...
        reporter = AWSTopicHistoryReporter(cmd.verbose)

        # HTTPClient...
        http_client = HTTPClient(False)

        # byline manager...
        byline_manager = BylineManager(http_client, api_auth)

        # message manager...
        message_manager = MessageManager(http_client, api_auth, reporter)

        if cmd.verbose:
            print("aws_topic_history: %s" % message_manager, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # start / end times...
        if cmd.latest:
            byline = byline_manager.find_latest_byline_for_topic(cmd.topic)

            if byline is None:
                exit(0)

            end = byline.rec
            start = byline.rec.timedelta(seconds=-0.1)

        elif cmd.timedelta:
            end = LocalizedDatetime.now()
            start = LocalizedDatetime(end - cmd.timedelta)

        else:
            end = LocalizedDatetime.now() if cmd.end is None else cmd.end
            start = cmd.start

        if cmd.verbose:
            print("aws_topic_history: start: %s" % start, file=sys.stderr)
            print("aws_topic_history: end: %s" % end, file=sys.stderr)
            sys.stderr.flush()

        # messages...
        try:
            for message in message_manager.find_for_topic(cmd.topic, start, end, cmd.rec_only):
                document = message if cmd.include_wrapper else message.payload

                print(JSONify.dumps(document))
                sys.stdout.flush()

        except HTTPException as ex:
            print("aws_topic_history: %s" % ex, file=sys.stderr)
            exit(1)


    # ----------------------------------------------------------------------------------------------------------------
    # end...
    except (ConnectionError, HTTPException) as ex:
        print("aws_topic_history: %s: %s" % (ex.__class__.__name__, ex), file=sys.stderr)

    except NetworkUnavailableException:
        print("aws_topic_history: network not available.", file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_topic_history: KeyboardInterrupt", file=sys.stderr)
