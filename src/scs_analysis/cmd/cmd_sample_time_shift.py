"""
Created on 3 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_core.data.timedelta import Timedelta


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleTimeShift(object):
    """
    unix command line handler
    """

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -t [[DD-]HH:]MM[:SS] [-v] [PATH]",
                                              version="%prog 1.0")

        # functions...
        self.__parser.add_option("--timedelta", "-t", type="string", nargs=1, action="store", dest="timedelta",
                                 help="offset in days / hours / minutes / seconds")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.timedelta is None:
            return False

        if self.timedelta is None:
            return False

        return True


    def is_valid_timedelta(self):
        if self.__opts.timedelta is None:
            return True

        return self.timedelta is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def timedelta(self):
        return Timedelta.construct_from_flag(self.__opts.timedelta)


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else 'rec'


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleTimeShift:{timedelta:%s, verbose:%s, path:%s}" % \
               (self.__opts.timedelta, self.verbose, self.path)
