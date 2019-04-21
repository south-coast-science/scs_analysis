"""
Created on 18 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdTimeshiftGrid(object):
    """unix command line handler"""

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -r START END STEP -t START END STEP -p FILENAME -f FILENAME "
                                                    "[-v] RH_PATH T_PATH REPORT_SUB_PATH REF_PATH",
                                                    version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--rh-offsets", "-r", type="int", nargs=3, action="store", dest="rh_offsets",
                                 help="START, END and STEP for humidity shifts (START <= END, STEP > 0)")

        self.__parser.add_option("--t-offsets", "-t", type="int", nargs=3, action="store", dest="t_offsets",
                                 help="START, END and STEP for temperature shifts (START <= END, STEP > 0)")

        self.__parser.add_option("--report-file", "-p", type="string", nargs=1, action="store", dest="report_filename",
                                 help="reported data filename")

        self.__parser.add_option("--ref-file", "-f", type="string", nargs=1, action="store", dest="ref_filename",
                                 help="reference data filename")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.rh_offsets is None or self.__opts.t_offsets is None:
            return False

        if self.report_filename is None or self.ref_filename is None:
            return False

        if len(self.__args) < 4:
            return False

        if self.rh_offset_start > self.rh_offset_end:
            return False

        if self.rh_offset_start < self.rh_offset_end and self.rh_offset_step < 1:
            return False

        if self.t_offset_start > self.t_offset_end:
            return False

        if self.t_offset_start < self.t_offset_end and self.t_offset_step < 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def rh_offset_start(self):
        return None if self.__opts.rh_offsets is None else self.__opts.rh_offsets[0]


    @property
    def rh_offset_end(self):
        return None if self.__opts.rh_offsets is None else self.__opts.rh_offsets[1]


    @property
    def rh_offset_step(self):
        return None if self.__opts.rh_offsets is None else self.__opts.rh_offsets[2]


    @property
    def t_offset_start(self):
        return None if self.__opts.t_offsets is None else self.__opts.t_offsets[0]


    @property
    def t_offset_end(self):
        return None if self.__opts.t_offsets is None else self.__opts.t_offsets[1]


    @property
    def t_offset_step(self):
        return None if self.__opts.t_offsets is None else self.__opts.t_offsets[2]


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def report_filename(self):
        return self.__opts.report_filename


    @property
    def ref_filename(self):
        return self.__opts.ref_filename


    @property
    def rh_path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def t_path(self):
        return self.__args[1] if len(self.__args) > 1 else None


    @property
    def report_sub_path(self):
        return self.__args[2] if len(self.__args) > 2 else None


    @property
    def ref_path(self):
        return self.__args[3] if len(self.__args) > 3 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdTimeshiftGrid:{rh_offsets:%s, t_offsets:%s, report_filename:%s, ref_filename:%s, verbose:%s, " \
               "rh_path:%s, t_path:%s, report_sub_path:%s, ref_path:%s}" % \
               (self.__opts.rh_offsets, self.__opts.t_offsets, self.report_filename, self.ref_filename, self.verbose,
                self.rh_path, self.t_path, self.report_sub_path, self.ref_path)
