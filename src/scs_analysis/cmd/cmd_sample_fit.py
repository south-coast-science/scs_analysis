"""
Created on 16 Feb 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_core.data.model_delta import ModelDelta


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleFit(object):
    """unix command line handler"""

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -i IND_PATH -d DEP_PATH_1 [-l LOWER_BOUND] [-u UPPER_BOUND]"
                                                    " [-p IND_PRECISION DEP_PRECISION] [-v]", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--ind-path", "-i", type="string", nargs=1, action="store", dest="ind_path",
                                 help="path to independent variable")

        self.__parser.add_option("--dep-path", "-d", type="string", nargs=1, action="store", dest="dep_path",
                                 help="path to dependent variable")

        # optional...
        self.__parser.add_option("--upper", "-u", type="float", nargs=1, action="store", dest="upper",
                                 help="upper bound of dataset")

        self.__parser.add_option("--lower", "-l", type="float", nargs=1, action="store", dest="lower",
                                 help="lower bound of dataset")

        self.__parser.add_option("--prec", "-p", type="int", nargs=2, action="store", dest="precisions",
                                 help="precision for independent and dependent variables (default 1, 3 decimals)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.ind_path is None or self.dep_path is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def ind_path(self):
        return self.__opts.ind_path


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
    def ind_prec(self):
        return ModelDelta.DEFAULT_INDEPENDENT_PREC if self.__opts.precisions is None else self.__opts.precisions[0]


    @property
    def dep_prec(self):
        return ModelDelta.DEFAULT_DEPENDENT_PREC if self.__opts.precisions is None else self.__opts.precisions[1]


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleFit:{ind_path:%s, dep_path:%s, lower:%s, upper:%s, precisions:%s, verbose:%s}" % \
               (self.ind_path, self.dep_path, self.lower, self.upper, self.__opts.precisions, self.verbose)
