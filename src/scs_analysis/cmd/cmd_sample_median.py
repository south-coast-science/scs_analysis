"""
Created on 16 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleMedian(object):
    """
    unix command line handler
    """

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-w SIZE] [-p PRECISION] [-v] PATH",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--window", "-w", type="int", nargs=1, action="store", dest="window", default=3,
                                 help="window size (must be an odd number, default 3)")

        self.__parser.add_option("--prec", "-p", type="int", nargs=1, action="store", default=None, dest="precision",
                                 help="precision (default 0 decimal places)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.window is not None and self.window % 2 == 0:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def window(self):
        return self.__opts.window


    @property
    def precision(self):
        return self.__opts.precision


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleMedian:{path:%s, window:%s, verbose:%s, precision:%s, args:%s}" % \
               (self.path, self.window, self.verbose, self.precision, self.args)
