"""
Created on 20 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVCollator(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -l LOWER_BOUND -u UPPER_BOUND -d DELTA [-f FILE_PREFIX] "
                                                    "[-v] PATH", version=version())

        # input...
        self.__parser.add_option("--lower", "-l", type="float", action="store", dest="lower",
                                 help="lower bound of dataset")

        self.__parser.add_option("--upper", "-u", type="float", action="store", dest="upper",
                                 help="upper bound of dataset")

        self.__parser.add_option("--delta", "-d", type="float", action="store", dest="delta",
                                 help="width of bin")

        # output...
        self.__parser.add_option("--file-prefix", "-f", type="string", action="store", dest="file_prefix",
                                 help="file prefix for collated CSVs")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.lower is None or self.upper is None or self.delta is None or self.path is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def lower(self):
        return self.__opts.lower


    @property
    def upper(self):
        return self.__opts.upper


    @property
    def delta(self):
        return self.__opts.delta


    @property
    def file_prefix(self):
        return self.__opts.file_prefix


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
        return "CmdCSVCollator:{lower:%s, upper:%s, delta:%s, file_prefix:%s, verbose:%s, path:%s}" % \
               (self.lower, self.upper, self.delta, self.file_prefix, self.verbose, self.path)
