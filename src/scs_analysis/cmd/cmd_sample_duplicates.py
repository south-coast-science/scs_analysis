"""
Created on 3 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleDuplicates(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ -x | -c }] [-v] [PATH]", version=version())

        # mode...
        self.__parser.add_option("--exclude", "-x", action="store_true", dest="exclude", default=False,
                                 help="output non-duplicate documents only")

        self.__parser.add_option("--counts", "-c", action="store_true", dest="counts", default=False,
                                 help="only list the count of matching documents")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.exclude and self.counts:
            return False

        if self.__args and len(self.__args) != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exclude(self):
        return self.__opts.exclude


    @property
    def counts(self):
        return self.__opts.counts


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
        return "CmdSampleDuplicates:{exclude:%s, counts:%s, verbose:%s, path:%s}" % \
            (self.exclude, self.counts, self.verbose, self.path)
