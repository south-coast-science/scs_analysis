#!/usr/bin/env python3

"""
Created on 6 Nov 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_topic_history utility is used to retrieve stored data from the South Coast Science / AWS historic data
retrieval system. Data can be retrieved by start or start + end localised datetimes, or by a days / hours / minutes
timedelta back in time from now.

Where start and end datetimes are used, messages are retrieved such that:

start datetime <= message rec datetime < end datetime

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
aws_topic_history.py [-c CREDENTIALS] { -l | -a LATEST_AT [-b BACK-OFF] | -t { [[DD-]HH:]MM[:SS] | :SS } |
-s START [-e END] } { -p HH:MM:SS [-m] [-x] | [-w] [-f] } [-r] [{ -v | -d }] TOPIC

EXAMPLES
aws_topic_history.py south-coast-science-dev/production-test/loc/1/gases -t 1 -v -w

DOCUMENT EXAMPLE - OUTPUT
{"device": "scs-bbe-401", "topic": "south-coast-science-demo/brighton/loc/1/climate", "upload": "2019-01-11T12:15:36Z",
"payload": {"val": {"hmd": 68.4, "tmp": 12.3}, "rec": "2019-01-11T12:15:36Z", "tag": "scs-bgx-401"}}

{"val": {"hmd": 68.4, "tmp": 12.3}, "rec": "2019-01-11T12:15:36Z", "tag": "scs-bgx-401"}

SEE ALSO
scs_analysis/aws_byline
scs_analysis/cognito_user_credentials

RESOURCES
https://github.com/curl/curl
"""

import sys

from scs_analysis.cmd.cmd_aws_topic_history import CmdAWSTopicHistory
from scs_analysis.handler.batch_download_reporter import BatchDownloadReporter

from scs_core.aws.manager.byline.byline_finder import BylineFinder
from scs_core.aws.manager.topic_history.topic_history_manager import TopicHistoryManager

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException
from scs_core.client.network import Network
from scs_core.client.resource_unavailable_exception import ResourceUnavailableException

from scs_core.data.checkpoint_generator import CheckpointGenerator
from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None
    reporter = None
    start_time = None

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
        logger.error("invalid format for checkpoint.")
        exit(2)

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

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

        # BylineFinder...
        byline_finder = BylineFinder()

        # MessageManager...
        reporter = BatchDownloadReporter()
        message_manager = TopicHistoryManager(reporter=reporter)


        # ------------------------------------------------------------------------------------------------------------
        # check...

        if not Network.is_available():
            logger.info("waiting for network")
            Network.wait()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        start_time = LocalizedDatetime.now()

        if cmd.latest_at:
            message = message_manager.find_latest_for_topic(auth.id_token, cmd.topic, cmd.latest_at, None,
                                                            cmd.include_wrapper, cmd.rec_only, None)

            if message:
                print(JSONify.dumps(message))

            exit(0)

        # start / end times...
        if cmd.latest:
            byline = byline_finder.find_latest_byline_for_topic(auth.id_token, cmd.topic)

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
        for message in message_manager.find_for_topic(auth.id_token, cmd.topic, start, end, None, cmd.fetch_last,
                                                      cmd.checkpoint, cmd.include_wrapper, cmd.rec_only, cmd.min_max,
                                                      cmd.exclude_remainder, False, None):
            print(JSONify.dumps(message))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except ResourceUnavailableException as ex:
        logger.error(repr(ex))
        exit(1)

    finally:
        if reporter:
            logger.info("blocks: %s" % reporter.block_count)

        if start_time:
            elapsed_time = LocalizedDatetime.now() - start_time
            logger.info("elapsed time: %s" % elapsed_time.as_json())
