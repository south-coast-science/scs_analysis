"""
Created on 11 Jan 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import sys

from scs_core.data.json import JSONify


# --------------------------------------------------------------------------------------------------------------------

class OSIOMQTTHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, mqtt_reporter, comms=None, echo=False):
        """
        Constructor
        """
        self.__reporter = mqtt_reporter
        self.__comms = comms
        self.__echo = echo


    # ----------------------------------------------------------------------------------------------------------------

    def handle(self, pub):
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
        return "OSIOMQTTClientHandler:{reporter:%s, comms:%s, echo:%s}" % (self.__reporter, self.__comms, self.__echo)
