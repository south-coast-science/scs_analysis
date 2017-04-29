#!/usr/bin/env python3

"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./osio_topic_retrieve.py -v /orgs/south-coast-science-dev/exhibition/loc/1/particulates -m1
"""

import sys

from scs_analysis.cmd.cmd_osio_topic_retrieve import CmdOSIOTopicRetrieve

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.manager.message_manager import MessageManager
from scs_core.sys.exception_report import ExceptionReport

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


# TODO: test whether topic is available

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOTopicRetrieve()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # APIAuth...
        api_auth = APIAuth.load_from_host(Host)

        if api_auth is None:
            print("APIAuth not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(api_auth, file=sys.stderr)
            sys.stderr.flush()

        # manager...
        manager = MessageManager(HTTPClient(), api_auth.api_key)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.use_offset():
            end = LocalizedDatetime.now()
            start = end.timedelta(minutes=-cmd.minutes)
        else:
            end = LocalizedDatetime.now() if cmd.end is None else cmd.end
            start = cmd.start

        messages = manager.find_for_topic(cmd.path, start, end)

        for message in messages:
            document = message if cmd.include_wrapping else message.payload.payload
            print(JSONify.dumps(document))

        if cmd.verbose:
            print("total: %d" % len(messages), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
