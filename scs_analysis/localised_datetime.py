#!/usr/bin/env python3

"""
Created on 14 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_mfr/osio_topic_list.py -p /orgs/south-coast-science-dev/uk -v
"""

import sys

from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.data.json import JSONify
from scs_core.osio.manager.topic_manager import TopicManager
from scs_core.osio.client.api_auth import APIAuth

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    # cmd = CmdOSIOTopicList()
    #
    # if cmd.verbose:
    #     print(cmd, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    pass
