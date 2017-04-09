#!/usr/bin/env python3

"""
Created on 14 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_mfr/osio_topic_list.py -p /orgs/south-coast-science-dev/uk -v
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

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOTopicList()

    if cmd.verbose:
        print(cmd, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # APIAuth...
    api_auth = APIAuth.load_from_host(Host)

    if api_auth is None:
        print("APIAuth not available.", file=sys.stderr)
        exit()

    if cmd.verbose:
        print(api_auth, file=sys.stderr)

    # manager...
    manager = TopicManager(HTTPClient(), api_auth.api_key)


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    topics = manager.find_for_org(api_auth.org_id)

    for topic in topics:
        if topic.path.startswith(cmd.path):
            print(JSONify.dumps(topic))
