"""
Created on 16 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleWeCSens(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-v] -s SENS PATH", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--sens", "-s", type="float", nargs=1, action="store", default=None, dest="sens",
                                 help="sensitivity (mV / ppb)")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.sens is None or len(self.__args) != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def sens(self):
        return self.__opts.sens


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
        return "CmdSampleWeCSens:{sens:%s, verbose:%s, path:%s}" % (self.sens, self.verbose, self.path)
