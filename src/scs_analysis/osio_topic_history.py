#!/usr/bin/env python3

"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The osio_topic_history utility is used to retrieve stored data from the OpenSensors.io Community Edition data
infrastructure. Data can be retrieved by start or start + end localised date / times, or by minutes backwards from now.

An OpenSensors.io API auth document must be installed on the host for the osio_mqtt_client
to operate. A specification should be obtained from the user's OpenSensors.io account.

SYNOPSIS
osio_topic_history.py { -m MINUTES | -s START [-e END] } [-p SECONDS] [-w] [-v] PATH

EXAMPLES
osio_topic_history.py -v /orgs/south-coast-science-dev/exhibition/loc/1/particulates -m1

FILES
~/SCS/osio/osio_api_auth.json

SEE ALSO
scs_analysis/osio_api_auth
"""

import sys

from scs_analysis.cmd.cmd_osio_topic_history import CmdOSIOTopicHistory

from scs_core.client.http_client import HTTPClient

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.manager.topic_manager import TopicManager
from scs_core.osio.manager.message_manager import MessageManager

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOTopicHistory()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("osio_topic_history: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # APIAuth...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            print("osio_topic_history: APIAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("osio_topic_history: %s" % api_auth, file=sys.stderr)
            sys.stderr.flush()

        # HTTPClient...
        http_client = HTTPClient(False)

        # topic manager...
        topic_manager = TopicManager(http_client, api_auth.api_key)

        # message manager...
        message_manager = MessageManager(http_client, api_auth.api_key, cmd.verbose)

        if cmd.verbose:
            print("osio_topic_history: %s" % message_manager, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # check topics...
        if not topic_manager.find(cmd.path):
            print("osio_topic_history: Topic not available: %s" % cmd.path, file=sys.stderr)
            exit(1)

        # time...
        if cmd.use_offset():
            end = LocalizedDatetime.now()
            start = end.timedelta(minutes=-cmd.minutes)
        else:
            end = LocalizedDatetime.now() if cmd.end is None else cmd.end
            start = cmd.start

        if cmd.verbose:
            print("osio_topic_history: start: %s" % start, file=sys.stderr)
            print("osio_topic_history: end: %s" % end, file=sys.stderr)
            sys.stderr.flush()

        # messages...
        messages = message_manager.find_for_topic(cmd.path, start, end, cmd.pause)

        for message in messages:
            document = message if cmd.include_wrapping else message.payload.content
            print(JSONify.dumps(document))
            sys.stdout.flush()

        if cmd.verbose:
            print("osio_topic_history: total: %d" % len(messages), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("osio_topic_history: KeyboardInterrupt", file=sys.stderr)
