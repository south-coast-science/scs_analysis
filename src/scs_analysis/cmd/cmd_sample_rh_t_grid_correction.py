"""
Created on 18 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleRhTGridCorrection(object):
    """unix command line handler"""


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -m B2 B1 B0 -c B2 B1 B0 [-r REFERENCE_PATH] [-v] "
                                                    "RH_PATH T_PATH REPORT_SUB_PATH", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--mT-weights", "-m", type="float", nargs=3, action="store", dest="mt",
                                 help="coefficients for sensitivity (highest first)")

        self.__parser.add_option("--cT-weights", "-c", type="float", nargs=3, action="store", dest="ct",
                                 help="coefficients for offset (highest first)")

        # optional...
        self.__parser.add_option("--r2", "-r", type="string", nargs=1, action="store", dest="r2",
                                 help="report R squared against REFERENCE instead of outputting data")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.mt is None or self.__opts.ct is None:
            return False

        if len(self.__args) < 3:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def mt_weights(self):
        return self.__opts.mt


    @property
    def mt_b2(self):
        return None if self.__opts.mt is None else self.__opts.mt[0]


    @property
    def mt_b1(self):
        return None if self.__opts.mt is None else self.__opts.mt[1]


    @property
    def mt_b0(self):
        return None if self.__opts.mt is None else self.__opts.mt[2]


    @property
    def ct_weights(self):
        return self.__opts.ct


    @property
    def ct_b2(self):
        return None if self.__opts.ct is None else self.__opts.ct[0]


    @property
    def ct_b1(self):
        return None if self.__opts.ct is None else self.__opts.ct[1]


    @property
    def ct_b0(self):
        return None if self.__opts.ct is None else self.__opts.ct[2]


    @property
    def r2(self):
        return self.__opts.r2 is not None


    @property
    def reference_path(self):
        return self.__opts.r2


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def rh_path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def t_path(self):
        return self.__args[1] if len(self.__args) > 1 else None


    @property
    def report_sub_path(self):
        return self.__args[2] if len(self.__args) > 2 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleRhTGridCorrection:{mt:%s, ct:%s, r2:%s, verbose:%s, " \
               "rh_path:%s, t_path:%s, report_sub_path:%s, reference_path:%s}" % \
               (self.__opts.mt, self.__opts.ct, self.r2, self.verbose,
                self.rh_path, self.t_path, self.report_sub_path, self.reference_path)
