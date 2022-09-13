"""
Created on 23 Oct 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleSlope(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -n NAME [-i ISO] [-t TALLY] [-x] [-p PRECISION] [-v] PATH",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--name", "-n", type="string", nargs=1, action="store", dest="name",
                                 help="slope field name (i.e. '1min')")

        # optional...
        self.__parser.add_option("--iso-path", "-i", type="string", nargs=1, action="store", default="rec", dest="iso",
                                 help="path for ISO 8601 datetime field (default 'rec')")

        self.__parser.add_option("--tally", "-t", type="int", nargs=1, action="store", default=2, dest="tally",
                                 help="compute for rolling TALLY number of data points (default 2)")

        self.__parser.add_option("--exclude-incomplete", "-x", action="store_true", dest="exclude_incomplete",
                                 default=False, help="exclude incomplete tallies")

        self.__parser.add_option("--prec", "-p", type="int", nargs=1, action="store", default=6, dest="precision",
                                 help="precision (default 6 decimal places)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.name is None:
            return False

        if self.tally < 1:
            return False

        if self.path is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def name(self):
        return self.__opts.name


    @property
    def iso(self):
        return self.__opts.iso


    @property
    def tally(self):
        return self.__opts.tally


    @property
    def exclude_incomplete(self):
        return self.__opts.exclude_incomplete


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
        return "CmdSampleSlope:{name:%s, iso:%s, tally:%s, exclude_incomplete:%s, precision:%s, verbose:%s, " \
               "path:%s}" % \
               (self.name, self.iso, self.tally, self.exclude_incomplete, self.precision, self.verbose,
                self.path)
