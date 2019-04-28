"""
Created on 16 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleWeCSens(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-v] T_PATH REPORT_SUB_PATH", version="%prog 1.0")

        # compulsory...
        # self.__parser.add_option("--sens", "-s", type="float", nargs=1, action="store", default=None, dest="sens",
        #                          help="sensitivity (mV / ppb)")

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
    def t_path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def report_sub_path(self):
        return self.__args[1] if len(self.__args) > 1 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleWeCSens:{verbose:%s, path:%s, path:%s}" % (self.verbose, self.t_path, self.report_sub_path)
