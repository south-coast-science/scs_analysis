"""
Created on 22 Aug 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleMdAPE(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-p PRECISION] [-e] [-v] REFERENCE_PATH PREDICTION_PATH",
                                              version=version())

        # output...
        self.__parser.add_option("--prec", "-p", type="int", action="store", default=3, dest="precision",
                                 help="precision (default 3 decimal places)")

        self.__parser.add_option("--errors", "-e", action="store_true", dest="errors", default=False,
                                 help="output the error values")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if len(self.__args) != 2:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def errors(self):
        return self.__opts.errors


    @property
    def precision(self):
        return self.__opts.precision


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def reference_path(self):
        return self.__args[0] if self.__args else None


    @property
    def prediction_path(self):
        return self.__args[1] if self.__args else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleMdAPE:{precision:%s, errors:%s, verbose:%s, paths:%s}" % \
                    (self.precision, self.errors, self.verbose, self.__args)
