"""
Created on 26 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_core.data.datum import Datum


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleSubset(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -i | -n  | -s } { [-e EQUAL] | [-l LOWER] [-u UPPER] } "
                                                    "[-s] [-x] [-v] PATH", version="%prog 1.0")

        # interpretation...
        self.__parser.add_option("--iso8601", "-i", action="store_true", dest="iso8601", default=False,
                                 help="interpret the value as an ISO 8601 datetime")

        self.__parser.add_option("--numeric", "-n", action="store_true", dest="numeric", default=False,
                                 help="interpret the value as a number")

        self.__parser.add_option("--string", "-s", action="store_true", dest="string", default=False,
                                 help="interpret the value as a string")

        self.__parser.add_option("--strict", "-t", action="store_true", dest="strict", default=False,
                                 help="halt on type errors")

        # optional...
        self.__parser.add_option("--equal", "-e", type="string", nargs=1, action="store", dest="equal",
                                 help="equal to")

        self.__parser.add_option("--lower", "-l", type="string", nargs=1, action="store", dest="lower",
                                 help="lower bound")

        self.__parser.add_option("--upper", "-u", type="string", nargs=1, action="store", dest="upper",
                                 help="upper bound")

        self.__parser.add_option("--exclusions", "-x", action="store_true", dest="exclusions", default=False,
                                 help="output exclusions instead of inclusions")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.iso8601:
            count += 1

        if self.numeric:
            count += 1

        if self.string:
            count += 1

        if count != 1:
            return False

        if self.equal is not None and (self.lower is not None or self.upper is not None):
            return False

        if self.lower is not None and self.upper is not None and self.upper <= self.lower:
            return False

        if len(self.__args) != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def inclusions(self):
        return not self.exclusions


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def iso8601(self):
        return self.__opts.iso8601


    @property
    def numeric(self):
        return self.__opts.numeric


    @property
    def string(self):
        return self.__opts.string


    @property
    def strict(self):
        return self.__opts.strict


    @property
    def equal(self):
        return self.__cast(self.__opts.equal)


    @property
    def lower(self):
        return self.__cast(self.__opts.lower)


    @property
    def upper(self):
        return self.__cast(self.__opts.upper)


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def exclusions(self):
        return self.__opts.exclusions


    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def __cast(self, value):
        if value is None:
            return None

        if self.string:
            return str(value)

        cast_value = Datum.datetime(value) if self.iso8601 else Datum.float(value)

        if cast_value is None:
            raise ValueError(value)

        return cast_value


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleSubset:{iso8601:%s, numeric:%s, string:%s, equal:%s, lower:%s, upper:%s, " \
               "strict:%s, exclusions:%s, verbose:%s, path:%s}" % \
               (self.iso8601, self.numeric, self.string, self.__opts.equal, self.__opts.lower, self.__opts.upper,
                self.strict, self.exclusions, self.verbose, self.path)
