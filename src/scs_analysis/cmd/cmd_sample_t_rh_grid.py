"""
Created on 16 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleTRhGrid(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -r MIN MAX STEP -t MIN MAX STEP { -w | -c | -d } [-v] "
                                                    "RH_PATH T_PATH REPORT_PATH, REF_PATH", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--rh", "-r", type="int", nargs=3, action="store", dest="rh",
                                 help="MIN, MAX and STEP for humidity deltas")

        self.__parser.add_option("--temp", "-t", type="int", nargs=3, action="store", dest="t",
                                 help="MIN, MAX and STEP for temperature deltas")

        self.__parser.add_option("--rh-rows", "-w", action="store_true", dest="rh_rows", default=False,
                                 help="report humidity rows, temperature columns")

        self.__parser.add_option("--rh-cols", "-c", action="store_true", dest="rh_cols", default=False,
                                 help="report temperature rows, humidity columns")

        self.__parser.add_option("--stdev", "-d", action="store_true", dest="stdev", default=False,
                                 help="report average standard deviation")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.rh is None or self.__opts.t is None:
            return False

        if self.rh_path is None or self.t_path is None:
            return False

        count = 0

        if self.rh_rows:
            count += 1

        if self.rh_cols:
            count += 1

        if self.stdev:
            count += 1

        if count != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def rh_min(self):
        return None if self.__opts.rh is None else self.__opts.rh[0]


    @property
    def rh_max(self):
        return None if self.__opts.rh is None else self.__opts.rh[1]


    @property
    def rh_step(self):
        return None if self.__opts.rh is None else self.__opts.rh[2]


    @property
    def t_min(self):
        return None if self.__opts.t is None else self.__opts.t[0]


    @property
    def t_max(self):
        return None if self.__opts.t is None else self.__opts.t[1]


    @property
    def t_step(self):
        return None if self.__opts.t is None else self.__opts.t[2]


    @property
    def rh_rows(self):
        return self.__opts.rh_rows


    @property
    def rh_cols(self):
        return self.__opts.rh_cols


    @property
    def stdev(self):
        return self.__opts.stdev


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
    def report_path(self):
        return self.__args[2] if len(self.__args) > 2 else None


    @property
    def ref_path(self):
        return self.__args[3] if len(self.__args) > 3 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleTRhGrid:{rh:%s, t:%s, rh_rows:%s, rh_cols:%s, stdev:%s, verbose:%s, " \
               "rh_path:%s, t_path:%s, report_path:%s, ref_path:%s}" % \
               (self.__opts.rh, self.__opts.t, self.rh_rows, self.rh_cols, self.stdev, self.verbose,
                self.rh_path, self.t_path, self.report_path, self.ref_path)
