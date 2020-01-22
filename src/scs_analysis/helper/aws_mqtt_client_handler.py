"""
Created on 11 Jan 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import json
import sys

from collections import OrderedDict

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

    def handle(self, _client, _userdata, message):
        payload = message.payload.decode()
        jdict = json.loads(payload, object_pairs_hook=OrderedDict)

        pub = Publication(message.topic, jdict) if self.__include_wrapper else jdict

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
