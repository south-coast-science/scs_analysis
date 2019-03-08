"""
Created on 11 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleRecord(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-v] [PATH]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.path is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

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
        return "CmdSampleRecord:{verbose:%s, path:%s}" % (self.verbose, self.path)
