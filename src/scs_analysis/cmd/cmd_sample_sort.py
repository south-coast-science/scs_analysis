"""
Created on 19 Sep 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleSort(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-r] [-v] SORT_PATH_1 [...SORT_PATH_N]", version=version())

        # function...
        self.__parser.add_option("--reverse", "-r", action="store_true", dest="reverse", default=False,
                                 help="sort in reverse order")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if len(self.__args) < 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def reverse(self):
        return self.__opts.reverse


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def sort_paths(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return ("CmdSampleSort:{reverse:%s, verbose:%s, sort_paths:%s}" %
                (self.reverse, self.verbose, self.sort_paths))
