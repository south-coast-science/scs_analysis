"""
Created on 15 Apr 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleCollator(object):
    """unix command line handler"""

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -x IND_PATH [-n NAME] -y DEP_PATH "
                                                    "[-l LOWER_BOUND] -u UPPER_BOUND -d DELTA [-v]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--ind-path", "-x", type="string", nargs=1, action="store", dest="ind_path",
                                 help="path to independent variable")

        self.__parser.add_option("--name", "-n", type="string", nargs=1, action="store", dest="name",
                                 help="name of the independent variable")

        self.__parser.add_option("--dep-path", "-y", type="string", nargs=1, action="store", dest="dep_path",
                                 help="path to dependent variable")

        self.__parser.add_option("--upper", "-u", type="int", nargs=1, action="store", dest="upper",
                                 help="upper bound of dataset")

        self.__parser.add_option("--delta", "-d", type="int", nargs=1, action="store", dest="delta",
                                 help="width of column domain")

        # optional...
        self.__parser.add_option("--lower", "-l", type="int", nargs=1, action="store", dest="lower", default=0,
                                 help="lower bound of dataset (default 0)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.ind_path is None or self.dep_path is None or \
                self.lower is None or self.upper is None or self.delta is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def ind_path(self):
        return self.__opts.ind_path


    @property
    def name(self):
        return self.__opts.name


    @property
    def dep_path(self):
        return self.__opts.dep_path


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
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleCollator:{ind_path:%s, name:%s, dep_path:%s, lower:%s, upper:%s, delta:%s, verbose:%s}" % \
               (self.ind_path, self.name, self.dep_path, self.lower, self.upper, self.delta, self.verbose)
