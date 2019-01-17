#!/usr/bin/env python3

"""
Created on 6 Nov 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The aws_topic_history utility is used to retrieve stored data from the South Coast Science / AWS historic data
retrieval system. Data can be retrieved by start or start + end localised date / times, or by an hours / minutes
timedelta from now. A further "latest" mode returns the most recent document, or none if the topic has never
received a publication.

Note that no check is made for the existence of the topic - if the topic does not exist, then no error is raised and
no data is returned.

SYNOPSIS
aws_topic_history.py { -l | -t [[DD-]HH:]MM  | -s START [-e END] } [-w] [-v] TOPIC

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
"""

import sys
import time

from scs_analysis.cmd.cmd_aws_topic_history import CmdAWSTopicHistory

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.manager.byline_manager import BylineManager
from scs_core.aws.manager.lambda_message_manager import MessageManager

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sys.http_exception import HTTPException

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


# TODO: move Reporter to handler package

# --------------------------------------------------------------------------------------------------------------------
# reporter...

class AWSTopicHistoryReporter(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, verbose):
        """
        Constructor
        """
        self.__verbose = verbose

        self.__document_count = 0
        self.__start_time = time.time()


    # ----------------------------------------------------------------------------------------------------------------

    def print(self, block_start, block_length):
        if not self.__verbose:
            return

        self.__document_count += block_length
        elapsed_time = round(time.time() - self.__start_time, 1)

        print("aws_topic_history: block start:%s docs:%d elapsed:%0.1f" %
              (block_start, self.__document_count, elapsed_time), file=sys.stderr)

        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSTopicHistoryReporter:{verbose:%s, document_count:%d, start_time:%d}" % \
               (self.__verbose, self.__document_count, self.__start_time)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSTopicHistory()

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

        # byline manager...
        byline_manager = BylineManager(HTTPClient(), api_auth)

        # message manager...
        message_manager = MessageManager(HTTPClient(), api_auth, reporter)

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
            start = end - cmd.timedelta

        else:
            end = LocalizedDatetime.now() if cmd.end is None else cmd.end
            start = cmd.start

        if cmd.verbose:
            print("aws_topic_history: start: %s" % start, file=sys.stderr)
            print("aws_topic_history: end: %s" % end, file=sys.stderr)
            sys.stderr.flush()

        # messages...
        try:
            for message in message_manager.find_for_topic(cmd.topic, start, end):
                document = message if cmd.include_wrapper else message.payload

                print(JSONify.dumps(document))
                sys.stdout.flush()

        except HTTPException as ex:
            print("aws_topic_history: %s" % ex, file=sys.stderr)
            exit(1)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_topic_history: KeyboardInterrupt", file=sys.stderr)
