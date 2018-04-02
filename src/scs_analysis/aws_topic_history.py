#!/usr/bin/env python3

"""
Created on 6 Nov 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The aws_topic_history utility is used to retrieve stored data from the South Coast Science / AWS data infrastructure.
Data can be retrieved by start or start + end localised date / times, or by minutes backwards from now.

Note that no check is made for the existence of the topic - if the topic does not exist, then no error is raised and
no data is returned.

EXAMPLES
./aws_topic_history.py south-coast-science-dev/production-test/loc/1/gases -m1 -v -w
"""

import sys

from scs_analysis.cmd.cmd_aws_topic_history import CmdAWSTopicHistory

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.manager.message_manager import MessageManager

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


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
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # APIAuth...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            print("aws_topic_history: APIAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print(api_auth, file=sys.stderr)
            sys.stderr.flush()

        # message manager...
        message_manager = MessageManager(HTTPClient(), api_auth, cmd.verbose)

        if cmd.verbose:
            print(message_manager, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # time...
        if cmd.use_offset():
            end = LocalizedDatetime.now()
            start = end.timedelta(minutes=-cmd.minutes)
        else:
            end = LocalizedDatetime.now() if cmd.end is None else cmd.end
            start = cmd.start

        if cmd.verbose:
            print("start: %s" % start, file=sys.stderr)
            print("end: %s" % end, file=sys.stderr)
            sys.stderr.flush()

        # messages...
        messages = message_manager.find_for_topic(cmd.path, start, end)

        for message in messages:
            document = message if cmd.include_wrapping else message.payload
            print(JSONify.dumps(document))

        if cmd.verbose:
            print("total: %d" % len(messages), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_topic_history: KeyboardInterrupt", file=sys.stderr)
