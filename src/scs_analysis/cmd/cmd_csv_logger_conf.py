"""
Created on 18 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVLoggerConf(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { [-r ROOT_PATH] [-o DELETE_OLDEST] [-i WRITE_INTERVAL] | "
                                                    "-d } [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--root", "-r", type="string", nargs=1, action="store", dest="root_path",
                                 help="set filesystem logging directory")

        self.__parser.add_option("--del-oldest", "-o", type="int", nargs=1, action="store", dest="delete_oldest",
                                 help="delete oldest logs to recover space (1) or stop when full (0)")

        self.__parser.add_option("--write-int", "-i", type="int", nargs=1, action="store", dest="write_interval",
                                 help="write interval in seconds (0 for immediate writes)")

        self.__parser.add_option("--delete", "-d", action="store_true", dest="delete",
                                 help="delete the logger configuration")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.set() and self.delete is not None:
            return False

        if self.write_interval is not None and self.write_interval < 0:
            return False

        return True


    def is_complete(self):
        if self.root_path is None or self.delete_oldest is None or self.write_interval is None:
            return False

        return True


    def set(self):
        if self.root_path is not None or self.delete_oldest is not None or self.write_interval is not None:
            return True

        return False


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def root_path(self):
        return self.__opts.root_path


    @property
    def delete_oldest(self):
        return None if self.__opts.delete_oldest is None else bool(self.__opts.delete_oldest)


    @property
    def write_interval(self):
        return self.__opts.write_interval


    @property
    def delete(self):
        return self.__opts.delete


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCSVLoggerConf:{root_path:%s, delete_oldest:%s, write_interval:%s, delete:%s, " \
               "verbose:%s}" % \
               (self.root_path, self.delete_oldest, self.write_interval, self.delete,
                self.verbose)
