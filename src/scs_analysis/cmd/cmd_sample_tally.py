"""
Created on 22 Aug 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleTally(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-t TALLY] [-p PRECISION] [-v] [PATH]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--tally", "-t", type="int", nargs=1, action="store", dest="tally",
                                 help="generate a rolling aggregate for TALLY number of data points (default all)")

        self.__parser.add_option("--prec", "-p", type="int", nargs=1, action="store", default=None, dest="precision",
                                 help="precision (default 0 decimal places)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.tally is not None and self.tally < 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def tally(self):
        return self.__opts.tally


    @property
    def precision(self):
        return self.__opts.precision


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleTally:{tally:%s, precision:%s, verbose:%s, path:%s}" % \
                    (self.tally, self.precision, self.verbose, self.path)
