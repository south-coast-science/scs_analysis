#!/usr/bin/env python3

"""
Created on 14 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_analysis/osio_topic_list.py -p /orgs/south-coast-science-dev/uk -v
"""

import sys

from scs_analysis.cmd.cmd_osio_topic_list import CmdOSIOTopicList

from scs_core.data.json import JSONify
from scs_core.osio.manager.topic_manager import TopicManager
from scs_core.osio.client.api_auth import APIAuth

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOTopicList()

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

        manager = TopicManager(http_client, auth.api_key)

        topics = manager.find_for_org(auth.org_id)

        for topic in topics:
            if topic.path.startswith(cmd.path):
                print(JSONify.dumps(topic))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("osio_topic_list: KeyboardInterrupt", file=sys.stderr)
