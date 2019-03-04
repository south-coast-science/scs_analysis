"""
Created on 2 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVReader(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c] [-l LIMIT] [-a] [-v] [FILENAME_1 .. FILENAME_N]",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--cast", "-c", action="store_true", dest="cast", default=False,
                                 help="cast values to numeric, where possible")

        self.__parser.add_option("--limit", "-l", type="int", nargs=1, action="store", dest="limit",
                                 help="output a maximum of LIMIT rows")

        self.__parser.add_option("--array", "-a", action="store_true", dest="array", default=False,
                                 help="output JSON documents as array instead of a sequence")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def cast(self):
        return self.__opts.cast


    @property
    def limit(self):
        return self.__opts.limit


    @property
    def array(self):
        return self.__opts.array


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def filenames(self):
        return self.__args if len(self.__args) > 0 else [None]


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCSVReader:{cast:%s, limit:%s, array:%s, verbose:%s, filenames:%s}" % \
               (self.cast, self.limit, self.array, self.verbose, self.filenames)
