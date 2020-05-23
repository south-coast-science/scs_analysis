"""
Created on 10 Mar 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_core.data.timedelta import Timedelta


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVSegmentor(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -m { [[DD-]HH:]MM[:SS] | :SS } [-i ISO] [-f FILE_PREFIX] "
                                                    "[-v]", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--max-interval", "-m", type="string", nargs=1, action="store", dest="max_interval",
                                 help="maximum permitted interval")

        # optional...
        self.__parser.add_option("--iso-path", "-i", type="string", nargs=1, action="store", default="rec", dest="iso",
                                 help="path for ISO 8601 datetime field (default 'rec')")

        self.__parser.add_option("--file-prefix", "-f", type="string", nargs=1, action="store", dest="file_prefix",
                                 help="file prefix for contiguous CSVs")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.max_interval is None:
            return False

        return True


    def is_valid_interval(self):
        if self.__opts.max_interval is None:
            return True

        return self.max_interval is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def max_interval(self):
        return Timedelta.construct_from_flag(self.__opts.max_interval)


    @property
    def iso(self):
        return self.__opts.iso


    @property
    def file_prefix(self):
        return self.__opts.file_prefix


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCSVSegmentor:{max_interval:%s, iso:%s, file_prefix:%s, verbose:%s}" % \
               (self.__opts.max_interval, self.iso, self.file_prefix, self.verbose)
