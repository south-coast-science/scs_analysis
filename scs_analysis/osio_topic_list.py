#!/usr/bin/env python3

"""
Created on 14 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_analysis/osio_topic_list.py south-coast-science-dev -p /orgs/south-coast-science-dev/uk -v
"""

import sys

from scs_analysis.cmd.cmd_topic_list import CmdTopicList

from scs_core.data.json import JSONify
from scs_core.osio.finder.topic_finder import TopicFinder
from scs_core.osio.client.api_auth import APIAuth

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdTopicList()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        http_client = HTTPClient()

        auth = APIAuth.load_from_host(Host)

        if cmd.verbose:
            print(auth, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        finder = TopicFinder(http_client, auth.api_key)

        topics = finder.find_for_org(cmd.org_id)

        for topic in topics:
            if topic.path.startswith(cmd.path):
                print(JSONify.dumps(topic))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("osio_topic_list: KeyboardInterrupt", file=sys.stderr)
