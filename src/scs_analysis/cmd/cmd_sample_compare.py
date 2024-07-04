"""
Created on 11 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version

from scs_core.data.datetime import LocalizedDatetime


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleCompare(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ -n | -i }] [-v] PATH", version=version())

        # input...
        self.__parser.add_option("--number", "-n", action="store_true", dest="number", default=False,
                                 help="interpret values as numbers")

        self.__parser.add_option("--iso8601", "-i", action="store_true", dest="iso8601", default=False,
                                 help="interpret values as ISO 8601 datetimes")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.number and self.iso8601:
            return False

        if len(self.__args) != 1:
            return False

        return True


    def value(self, scalar):
        if self.number:
            try:
                return float(scalar)
            except (TypeError, ValueError):
                return None

        if self.iso8601:
            return LocalizedDatetime.construct_from_iso8601(scalar)

        return scalar


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def number(self):
        return self.__opts.number


    @property
    def iso8601(self):
        return self.__opts.iso8601


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
        return "CmdSampleCompare:{number:%s, iso8601:%s, verbose:%s, path:%s}" % \
                (self.number, self.iso8601, self.verbose, self.path)
