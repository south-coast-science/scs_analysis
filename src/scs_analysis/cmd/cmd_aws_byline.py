"""
Created on 25 Dec 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSByline(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -d DEVICE | -t TOPIC } [-v]", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--device", "-d", type="string", nargs=1, action="store", dest="device",
                                 help="device tag")

        self.__parser.add_option("--topic", "-t", type="string", nargs=1, action="store", dest="topic",
                                 help="topic path")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.device) == bool(self.topic):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def device(self):
        return self.__opts.device


    @property
    def topic(self):
        return self.__opts.topic


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSByline:{device:%s, topic:%s, verbose:%s}" % (self.device, self.topic, self.verbose)
