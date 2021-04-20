"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdConfigurationMonitor(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-t TAG] [{ -o | -h }] [-i INDENT] [-v]",
                                              version="%prog 1.0")

        # filters..
        self.__parser.add_option("--tag", "-t", type="string", action="store", dest="tag",
                                 help="the (partial) tag of the device(s)")

        # output..
        self.__parser.add_option("--tags-only", "-o", action="store_true", dest="tags_only", default=False,
                                 help="report device tags only")

        self.__parser.add_option("--history", "-l", action="store_true", dest="history", default=False,
                                 help="report the history of one device")

        self.__parser.add_option("--indent", "-i", type="int", nargs=1, action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.tags_only and self.history:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def tag(self):
        return self.__opts.tag


    @property
    def tags_only(self):
        return self.__opts.tags_only


    @property
    def history(self):
        return self.__opts.history


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdConfigurationMonitor:{tag:%s, tags_only:%s, history:%s, verbose:%s}" % \
               (self.tag, self.tags_only, self.history, self.verbose)
