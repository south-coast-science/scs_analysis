"""
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleConv(object):
    """
    unix command line handler
    """

    def __init__(self):
        """stuff"""
        self.__parser = optparse.OptionParser(usage="%prog PATH -s SENSITIVITY [-v]", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--sensitivity", "-s", type="float", nargs=1, action="store", dest="sensitivity",
                                 help="sensitivity (mV / ppb)")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.path is None or self.sensitivity is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def sensitivity(self):
        return self.__opts.sensitivity


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
        return "CmdSampleConv:{sensitivity:%0.3f, verbose:%s, args:%s}" % \
                    (self.sensitivity, self.verbose, self.args)
