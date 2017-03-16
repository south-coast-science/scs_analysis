#!/usr/bin/env python3

"""
Created on 20 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_analysis/osio_topic_subscribe.py /users/southcoastscience-dev/test/status
"""

import sys

from scs_analysis.cmd.cmd_osio_topic import CmdOSIOTopic

from scs_core.data.json import JSONify
from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.manager.message_event_subscriber import MessageEventSubscriber
from scs_core.sys.exception_report import ExceptionReport

from scs_host.client.http_streaming_client import HTTPStreamingClient
from scs_host.sys.host import Host


# TODO: sort out exceptions on close

# --------------------------------------------------------------------------------------------------------------------

class OSIOTopicAgent(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def __local_listener(cls, event):
        datum = JSONify.dumps(event.message)

        print(datum)
        sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, path, verbose=False):
        """
        Constructor
        """
        # fields...
        self.__path = path
        self.__verbose = verbose

        self.__subscriber = None


    # ----------------------------------------------------------------------------------------------------------------

    def subscribe(self):
        client = HTTPStreamingClient()
        auth = APIAuth.load_from_host(Host)

        self.__subscriber = MessageEventSubscriber(client)
        self.__subscriber.subscribe(self.__local_listener, auth, self.__path)


    def close(self):
        self.__subscriber.close()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def verbose(self):
        return self.__verbose


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "OSIOTopicAgent:{path:%s, verbose:%s}" % (self.__path, self.verbose)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOTopic()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        agent = OSIOTopicAgent(cmd.path, cmd.verbose)

        if cmd.verbose:
            print(agent, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        agent.subscribe()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("osio_topic_subscribe: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        if not ex.__class__.__name__ == "error":                                    # TODO: needs cleaner handling
            print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        agent.close()
