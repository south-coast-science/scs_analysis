"""
Created on 20 Jun 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleRange(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-f] [-u] [-p PRECISION] [-v] SUB_NODE",
                                              version=version())

        # mode...
        self.__parser.add_option("--full", "-f", action="store_true", dest="full", default=False,
                                 help="report narrative to stderr")

        self.__parser.add_option("--upper", "-u", action="store_true", dest="upper", default=False,
                                 help="report narrative to stderr")

        # output...
        self.__parser.add_option("--prec", "-p", type="int", action="store", default=1, dest="precision",
                                 help="precision (default 1 decimal places)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if len(self.__args) != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def full(self):
        return self.__opts.full


    @property
    def upper(self):
        return self.__opts.upper


    @property
    def precision(self):
        return self.__opts.precision


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def sub_node(self):
        return self.__args[0]


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleRange:{full:%s, upper:%s, precision:%s, verbose:%s, sub_node:%s}" % \
                (self.full, self.upper, self.precision, self.verbose, self.sub_node)
