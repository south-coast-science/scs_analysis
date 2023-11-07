"""
Created on 2 Nov 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from glob import glob

from scs_analysis import version
from scs_core.data.model_delta import ModelDelta


# --------------------------------------------------------------------------------------------------------------------

class CmdCollationSummary(object):
    """unix command line handler"""

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog  -f FILE_PREFIX -i IND_PATH "
                                                    "[-p IND_PRECISION DEP_PRECISION] [-v] DEP_PATH_1 [..DEP_PATH_N]",
                                              version=version())

        # input...
        self.__parser.add_option("--file-prefix", "-f", type="string", action="store", dest="file_prefix",
                                 help="file prefix for collated CSVs")

        self.__parser.add_option("--ind-path", "-i", type="string", action="store", dest="ind_path",
                                 help="path to independent variable")

        # output...
        self.__parser.add_option("--prec", "-p", type="int", nargs=2, action="store", dest="precisions",
                                 help="precision for independent and dependent variables (default 1, 3 decimals)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.file_prefix is None or self.ind_path is None or len(self.dep_paths) < 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def file_prefix(self):
        return self.__opts.file_prefix


    @property
    def filenames(self):
        return [] if self.file_prefix is None else glob(self.file_prefix + '*.csv')


    @property
    def ind_path(self):
        return self.__opts.ind_path


    @property
    def ind_prec(self):
        return ModelDelta.DEFAULT_INDEPENDENT_PREC if self.__opts.precisions is None else self.__opts.precisions[0]


    @property
    def dep_prec(self):
        return ModelDelta.DEFAULT_DEPENDENT_PREC if self.__opts.precisions is None else self.__opts.precisions[1]


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def dep_paths(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCollationSummary:{file_prefix:%s, ind_path:%s, precisions:%s, verbose:%s, dep_paths:%s}" % \
               (self.file_prefix, self.ind_path, self.__opts.precisions, self.verbose, self.dep_paths)
