"""
Created on 27 Sep 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json
import sys

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify
from scs_core.data.publication import Publication, ReceivedPublication


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class AWSMQTTSubscriptionHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, reporter, comms=None, wrap=True, timed=False, echo=False):
        """
        Constructor
        """
        self.__reporter = reporter
        self.__comms = comms
        self.__wrap = wrap
        self.__timed = timed
        self.__echo = echo


    # ----------------------------------------------------------------------------------------------------------------

    def handle(self, _client, _userdata, message):
        payload = message.payload.decode()
        payload_jdict = json.loads(payload)

        publication = Publication(message.topic, payload_jdict) if self.__wrap else payload_jdict

        if self.__timed:
            publication = ReceivedPublication(LocalizedDatetime.now(), publication)

        try:
            self.__comms.connect()
            self.__comms.write(JSONify.dumps(publication), False)

        except ConnectionError:
            try:
                self.__reporter.print("handle: ConnectionError: %s." % self.__comms.address)
            except AttributeError:
                self.__reporter.print("handle: ConnectionError.")
                exit(0)

        finally:
            self.__comms.close()

        if self.__echo:
            print(JSONify.dumps(publication))
            sys.stdout.flush()

            self.__reporter.print("received: %s" % JSONify.dumps(publication))


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTSubscriptionHandler:{reporter:%s, comms:%s, wrap:%s, timed:%s, echo:%s}" % \
               (self.__reporter, self.__comms, self.__wrap, self.__timed, self.__echo)


