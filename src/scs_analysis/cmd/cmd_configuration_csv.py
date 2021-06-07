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
        self.__parser = optparse.OptionParser(usage="%prog { -l LATEST_CSV | -d HISTORIES_CSV_DIR } [-v]",
                                              version="%prog 1.0")

        # mode...
        self.__parser.add_option("--latest", "-l", type="string", action="store", dest="latest",
                                 help="retrieve latest configurations")

        self.__parser.add_option("--histories", "-d", type="string", action="store", dest="histories",
                                 help="retrieve configuration histories")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        return bool(self.latest) != bool(self.histories)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def latest(self):
        return self.__opts.latest


    @property
    def histories(self):
        return self.__opts.histories


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdConfigurationCSV:{latest:%s, histories:%s, verbose:%s}" %  \
               (self.latest, self.histories, self.verbose)
