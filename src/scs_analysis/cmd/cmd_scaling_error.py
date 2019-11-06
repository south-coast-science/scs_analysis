"""
Created on 6 Nov 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdScalingError(object):
    """
    unix command line handler
    """

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-p PRECISION] [-v] REFERENCE_PATH REPORTED_PATH ERROR_PATH",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--prec", "-p", type="int", nargs=1, action="store", default=3, dest="precision",
                                 help="precision (default 3 decimal place)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if len(self.__args) != 3:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def precision(self):
        return self.__opts.precision


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def reference_path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def reported_path(self):
        return self.__args[1] if len(self.__args) > 1 else None


    @property
    def error_path(self):
        return self.__args[2] if len(self.__args) > 2 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdScalingError:{precision:%s, verbose:%s, reference_path:%s, reported_path:%s, error_path:%s}" % \
               (self.precision, self.verbose, self.reference_path, self.reported_path, self.error_path)
