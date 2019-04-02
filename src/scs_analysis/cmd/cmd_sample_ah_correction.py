"""
Created on 1 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleAhCorrection(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -s SENS_MV BASELINE -c WS WB [-v] GAS_SUB_PATH AH_PATH",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--sensor", "-s", type="float", nargs=2, action="store", dest="sensor",
                                 help="sensitivity and baseline at aH 0")

        self.__parser.add_option("--correction", "-c", type="float", nargs=2, action="store", dest="correction",
                                 help="sensitivity and baseline weightings for a standard aH delta unit")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.sensor is None or self.__opts.correction is None:
            return False

        if len(self.__args) != 2:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def sens_mv(self):
        return None if self.__opts.sensor is None else self.__opts.sensor[0]


    @property
    def baseline_offset(self):
        return None if self.__opts.sensor is None else self.__opts.sensor[1]


    @property
    def ws(self):
        return None if self.__opts.correction is None else self.__opts.correction[0]


    @property
    def wb(self):
        return None if self.__opts.correction is None else self.__opts.correction[1]


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def gas_sub_path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def ah_path(self):
        return self.__args[1] if len(self.__args) > 1 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleAhCorrection:{sensor:%s, correction:%s, verbose:%s, paths:%s}" %  \
               (self.__opts.sensor, self.__opts.correction, self.verbose, self.__args)
