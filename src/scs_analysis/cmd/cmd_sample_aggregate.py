"""
Created on 24 Oct 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_airnow import version
from scs_core.data.timedelta import Timedelta


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleAggregate(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -c HH:MM:SS [-m] [-i ISO] [-r { [DD-]HH:MM[:SS] | :SS }] "
                                                    "[-x] [-v] [PATH_1 .. PATH_N]", version=version())

        # compulsory...
        self.__parser.add_option("--checkpoint", "-c", type="string", action="store", dest="checkpoint",
                                 help="a time specification i.e. **:/05:00")

        # optional...
        self.__parser.add_option("--min-max", "-m", action="store_true", dest="min_max", default=False,
                                 help="report min and max in addition to midpoint")

        self.__parser.add_option("--iso-path", "-i", type="string", action="store", default="rec", dest="iso",
                                 help="path for ISO 8601 datetime field (default 'rec')")

        self.__parser.add_option("--rule", "-r", type="string", action="store", dest="rule",
                                 help="apply 75% rule with sampling INTERVAL")

        self.__parser.add_option("--exclude-remainder", "-x", action="store_true", dest="exclude_remainder",
                                 help="ignore data points after the last complete period")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.checkpoint is None:
            return False

        return True


    def is_valid_interval(self):
        if self.__opts.rule is None:
            return True

        return self.interval is not None


    def ignore_rule(self):
        return self.__opts.rule is None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def checkpoint(self):
        return self.__opts.checkpoint


    @property
    def min_max(self):
        return self.__opts.min_max


    @property
    def iso(self):
        return self.__opts.iso


    @property
    def interval(self):
        return Timedelta.construct_from_flag(self.__opts.rule)


    @property
    def exclude_remainder(self):
        return self.__opts.exclude_remainder


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def nodes(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleAggregate:{checkpoint:%s, min_max:%s, iso:%s, interval:%s, exclude_remainder:%s, " \
               "verbose:%s, nodes:%s}" %  \
               (self.checkpoint, self.min_max, self.iso, self.interval, self.exclude_remainder,
                self.verbose, self.nodes)
