#!/usr/bin/env python3

"""
Created on 6 Nov 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_topic_history utility is used to retrieve stored data from the South Coast Science / AWS historic data
retrieval system. Data can be retrieved by start or start + end localised datetimes, or by a days / hours / minutes
timedelta back in time from now.

A latest mode returns the most recent document, or none if the topic has never received a publication. A --latest-at
mode returns the most recent document, or none, prior to, or at the given datetime.

The --rec-only flag causes only the rec fields on the documents to be returned. This results in much faster data
retrieval, and is useful if sampling continuity is being tested.

Note that no check is made for the existence of the topic - if the topic does not exist, then no error is raised and
no data is returned.

Equivalent to cURL:
curl "https://aws.southcoastscience.com/topicMessages?topic=south-coast-science-dev/production-test/loc/1/gases
&startTime=2018-12-13T07:03:59.712Z&endTime=2018-12-13T15:10:59.712Z"

SYNOPSIS
aws_topic_history.py { -l | -a LATEST_AT | -t { [[DD-]HH:]MM[:SS] | :SS } | -s START [-e END] }
{ -c HH:MM:SS [-m] [-x] | [-w] [-f] } [-r] [{ -v | -d }] TOPIC

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

from scs_core.client.network import Network
from scs_core.client.resource_unavailable_exception import ResourceUnavailableException

from scs_core.data.checkpoint_generator import CheckpointGenerator
from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None
    reporter = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSTopicHistory()

    Logging.config('aws_topic_history', level=cmd.log_level())
    logger = Logging.getLogger()

    if not cmd.is_valid_latest_at():
        logger.error("invalid format for latest-to datetime.")
        exit(2)

    if not cmd.is_valid_timedelta():
        logger.error("invalid format for timedelta.")
        exit(2)

    if not cmd.is_valid_start():
        logger.error("invalid format for start datetime.")
        exit(2)

    if not cmd.is_valid_end():
        logger.error("invalid format for end datetime.")
        exit(2)

    if cmd.checkpoint is not None and cmd.checkpoint != 'auto' and not CheckpointGenerator.is_valid(cmd.checkpoint):
        logger.error("invalid format for end datetime.")
        exit(2)

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # APIAuth...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            logger.error("APIAuth not available.")
            exit(1)

        logger.info(api_auth)

        # reporter...
        reporter = AWSTopicHistoryReporter(cmd.verbose)

        # byline manager...
        byline_manager = BylineManager(api_auth)

        # message manager...
        message_manager = MessageManager(api_auth, reporter)

        logger.info(message_manager)

        # ------------------------------------------------------------------------------------------------------------
        # check...

        if not Network.is_available():
            logger.info("waiting for network.")
            Network.wait()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.latest_at:
            message = message_manager.find_latest_for_topic(cmd.topic, cmd.latest_at, cmd.include_wrapper, cmd.rec_only)
            document = message if cmd.include_wrapper else message.payload

            if document:
                print(JSONify.dumps(document))

            exit(0)

        # start / end times...
        if cmd.latest:
            byline = byline_manager.find_latest_byline_for_topic(cmd.topic)

            if byline is None:
                exit(0)

            end = byline.rec.timedelta(seconds=1)
            start = byline.rec.timedelta(seconds=-1)        # TODO: should not need this

        elif cmd.timedelta:
            end = LocalizedDatetime.now()
            start = end - cmd.timedelta

        else:
            end = LocalizedDatetime.now() if cmd.end is None else cmd.end
            start = cmd.start

        logger.info("start: %s" % start)
        logger.info("end: %s" % end)

        # messages...
        for message in message_manager.find_for_topic(cmd.topic, start, end, cmd.fetch_last, cmd.checkpoint,
                                                      cmd.include_wrapper, cmd.rec_only,
                                                      cmd.min_max, cmd.exclude_remainder):
            print(JSONify.dumps(message))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (ConnectionError, HTTPException) as ex:
        logger.error("%s: %s" % (ex.__class__.__name__, ex))

    except ResourceUnavailableException as ex:
        logger.error(repr(ex))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        if reporter:
            logger.info("blocks: %s" % reporter.block_count)
