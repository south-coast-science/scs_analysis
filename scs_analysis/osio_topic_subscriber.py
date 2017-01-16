#!/usr/bin/env python3

"""
Created on 20 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./osio_topic_subscriber.py /users/southcoastscience-dev/test/json
"""

import sys

from scs_analysis.cmd.cmd_topic_subscriber import CmdTopicSubscriber

from scs_core.data.json import JSONify
from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.finder.message_event_subscriber import MessageEventSubscriber
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

    def __init__(self, topic, verbose=False):
        """
        Constructor
        """
        # fields...
        self.__topic = topic
        self.__verbose = verbose

        self.__subscriber = None


    # ----------------------------------------------------------------------------------------------------------------

    def subscribe(self):
        client = HTTPStreamingClient()
        auth = APIAuth.load(Host)

        self.__subscriber = MessageEventSubscriber(client)
        self.__subscriber.subscribe(self.__local_listener, auth, self.__topic)


    def close(self):
        self.__subscriber.close()


    # ----------------------------------------------------------------------------------------------------------------

    def __local_listener(self, event):
        datum = JSONify.dumps(event.message)

        print(datum)
        sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def verbose(self):
        return self.__verbose


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "OSIOTopicAgent:{verbose:%s}" % self.verbose


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    agent = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdTopicSubscriber()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        agent = OSIOTopicAgent(cmd.topic, cmd.verbose)

        if cmd.verbose:
            print(agent, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        agent.subscribe()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("osio_topic_subscriber: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        agent.close()
