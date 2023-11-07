"""
Created on 4 Mar 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleStats(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-t TAG] [-i] [-p PRECISION] [-a] [-r] [-v] "
                                                    "PATH_1 [..PATH_N]", version=version())

        # input...
        self.__parser.add_option("--tag", "-t", type="string", action="store", default='tag', dest="tag",
                                 help="name of the tag field (default 'tag')")

        # output...
        self.__parser.add_option("--include-tag", "-i", action="store_true", dest="include_tag", default=False,
                                 help="include the device tag")

        self.__parser.add_option("--prec", "-p", type="int", action="store", default=6, dest="precision",
                                 help="precision (default 6 decimal places)")

        self.__parser.add_option("--analytic", "-a", action="store_true", dest="analytic", default=False,
                                 help="analytic output")

        self.__parser.add_option("--rows", "-r", action="store_true", dest="rows", default=False,
                                 help="output results for each path on a separate row")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if not self.paths:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def tag(self):
        return self.__opts.tag


    @property
    def include_tag(self):
        return self.__opts.include_tag


    @property
    def precision(self):
        return self.__opts.precision


    @property
    def analytic(self):
        return self.__opts.analytic


    @property
    def rows(self):
        return self.__opts.rows


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def paths(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleStats:{tag:%s, include_tag:%s, precision:%s, analytic:%s, rows:%s, verbose:%s, paths:%s}" % \
               (self.tag, self.include_tag, self.precision, self.analytic, self.rows, self.verbose, self.paths)
