"""
Created on 7 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdConfigurationCSV(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -l LATEST_CSV | -d HISTORY_CSV_DIR } [-v]",
                                              version="%prog 1.0")

        # mode...
        self.__parser.add_option("--latest", "-l", type="string", action="store", dest="latest",
                                 help="retrieve latest configurations")

        self.__parser.add_option("--history", "-d", type="string", action="store", dest="history",
                                 help="retrieve configuration histories")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()

    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        return bool(self.latest) != bool(self.history)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def latest(self):
        return self.__opts.latest


    @property
    def history(self):
        return self.__opts.history


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdConfigurationCSV:{latest:%s, history:%s, verbose:%s}" %  (self.latest, self.history, self.verbose)
