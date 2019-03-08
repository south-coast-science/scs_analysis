"""
Created on 16 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleAH(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-v] RH_PATH T_PATH", version="%prog 1.0")

        # optional...
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
    def verbose(self):
        return self.__opts.verbose


    @property
    def rh_path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def t_path(self):
        return self.__args[1] if len(self.__args) > 1 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleAH:{verbose:%s, rh_path:%s, t_path:%s}" % (self.verbose, self.rh_path, self.t_path)
