#!/usr/bin/env python3

"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./osio_topic_history.py -v /orgs/south-coast-science-dev/exhibition/loc/1/particulates -m1
"""

import sys

from scs_analysis.cmd.cmd_topic_history import CmdTopicHistory

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.manager.topic_manager import TopicManager
from scs_core.osio.manager.message_manager import MessageManager

from scs_core.sys.exception_report import ExceptionReport

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


# TODO: catch and report the following error:

# ./osio_topic_history.py /orgs/south-coast-science-dev/alphasense/loc/303/gases -p 0.5 -v -s 2017-09-19T14:00:00+01:00 -e 2017-09-21T23:59:00+01:00

# {"cls": "ClientException", "args": [null], "trace": [
# {"loc": "File \"/Users/bruno/Documents/Development/Python/Mac/scs_core/scs_core/osio/client/rest_client.py\", line 57, in get", "stat": "response_jstr = self.__http_client.get(path, params, self.__headers)"},
# {"loc": "File \"/Users/bruno/Documents/Development/Python/Mac/scs_host_posix/scs_host/client/http_client.py\", line 58, in get", "stat": "raise HTTPException.construct(response, data)"},
# {"loc": "scs_core.sys.http_exception.HTTPException: HTTPException:{status:500, reason:Server Error, data:}", "stat": null},
# {"loc": "The above exception was the direct cause of the following exception:", "stat": null},
# {"loc": "Traceback (most recent call last):", "stat": null}, {"loc": "File \"./osio_topic_history.py\", line 94, in <module>", "stat": "messages = message_manager.find_for_topic(cmd.path, start, end, cmd.pause)"},
# {"loc": "File \"/Users/bruno/Documents/Development/Python/Mac/scs_core/scs_core/osio/manager/message_manager.py\", line 50, in find_for_topic", "stat": "for batch in self.__find(request_path, start_date, end_date):"},
# {"loc": "File \"/Users/bruno/Documents/Development/Python/Mac/scs_core/scs_core/osio/manager/message_manager.py\", line 76, in __find", "stat": "jdict = self.__rest_client.get(request_path, params)"},
# {"loc": "File \"/Users/bruno/Documents/Development/Python/Mac/scs_core/scs_core/osio/client/rest_client.py\", line 62, in get", "stat": "raise ClientException.construct(exc) from exc"}],
# "sum": "scs_core.osio.client.client_excepion.ClientException: ClientException:{error:None}"}


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdTopicHistory()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # APIAuth...
        api_auth = APIAuth.load_from_host(Host)

        if api_auth is None:
            print("APIAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print(api_auth, file=sys.stderr)
            sys.stderr.flush()

        # topic manager...
        topic_manager = TopicManager(HTTPClient(), api_auth.api_key)

        # message manager...
        message_manager = MessageManager(HTTPClient(), api_auth.api_key, cmd.verbose)

        if cmd.verbose:
            print(message_manager, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # check topics...
        if not topic_manager.find(cmd.path):
            print("Topic not available: %s" % cmd.path, file=sys.stderr)
            exit(1)

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
        messages = message_manager.find_for_topic(cmd.path, start, end, cmd.pause)

        for message in messages:
            document = message if cmd.include_wrapping else message.payload.payload
            print(JSONify.dumps(document))

        if cmd.verbose:
            print("total: %d" % len(messages), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("osio_topic_history: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
