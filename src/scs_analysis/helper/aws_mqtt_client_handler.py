"""
Created on 11 Jan 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json
import sys

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication


# --------------------------------------------------------------------------------------------------------------------

class AWSMQTTClientHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, mqtt_reporter, comms, include_wrapper, echo):
        """
        Constructor
        """
        self.__reporter = mqtt_reporter
        self.__comms = comms
        self.__include_wrapper = include_wrapper
        self.__echo = echo


    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyUnusedLocal

    def handle(self, client, userdata, message):
        payload = message.payload.decode()
        payload_jdict = json.loads(payload)

        pub = Publication(message.topic, payload_jdict) if self.__include_wrapper else payload_jdict

        try:
            self.__comms.connect()
            self.__comms.write(JSONify.dumps(pub), False)

        except ConnectionRefusedError:
            self.__reporter.print("connection refused for %s" % self.__comms.address)

        finally:
            self.__comms.close()

        if self.__echo:
            print(JSONify.dumps(pub))
            sys.stdout.flush()

        self.__reporter.print("received: %s" % JSONify.dumps(pub))


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTClientHandler:{reporter:%s, comms:%s, include_wrapper:%s, echo:%s}" % \
               (self.__reporter, self.__comms, self.__include_wrapper, self.__echo)
