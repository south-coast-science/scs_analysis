"""
Created on 15 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdNodeShift(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -o OFFSET [-f] [-v] SOURCE_PATH [TARGET_PATH]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--offset", "-o", type="int", nargs=1, action="store", dest="offset",
                                 help="number of documents of shift (negative is up)")

        # optional...
        self.__parser.add_option("--fill", "-f", action="store_true", dest="fill", default=False,
                                 help="report documents with missing inner values")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.offset is None or self.source_path is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def offset(self):
        return self.__opts.offset


    @property
    def fill(self):
        return self.__opts.fill


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def source_path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def target_path(self):
        return self.__args[1] if len(self.__args) > 1 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdNodeShift:{offset:%s, fill:%s, verbose:%s, source_path:%s, target_path:%s}" % \
               (self.offset, self.fill, self.verbose, self.source_path, self.target_path)
