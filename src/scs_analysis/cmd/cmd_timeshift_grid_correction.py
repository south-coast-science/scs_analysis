"""
Created on 22 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdTimeshiftGridCorrection(object):
    """unix command line handler"""

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -r OFFSET -t OFFSET -p FILENAME -f FILENAME "
                                                    "[-v] RH_PATH T_PATH REPORT_SUB_PATH REF_PATH",
                                                    version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--rh-offset", "-r", type="int", nargs=1, action="store", dest="rh_offset",
                                 help="OFFSET for humidity shift")

        self.__parser.add_option("--t-offset", "-t", type="int", nargs=1, action="store", dest="t_offset",
                                 help="OFFSET for temperature shift")

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
        if self.__opts.rh_offset is None or self.__opts.t_offset is None:
            return False

        if self.report_filename is None or self.ref_filename is None:
            return False

        if len(self.__args) < 4:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def rh_offset(self):
        return self.__opts.rh_offset


    @property
    def t_offset(self):
        return self.__opts.t_offset


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
        return "CmdTimeshiftGridCorrection:{rh_offset:%s, t_offset:%s, " \
               "report_filename:%s, ref_filename:%s, verbose:%s, " \
               "rh_path:%s, t_path:%s, report_sub_path:%s, ref_path:%s}" % \
               (self.__opts.rh_offset, self.__opts.t_offset,
                self.report_filename, self.ref_filename, self.verbose,
                self.rh_path, self.t_path, self.report_sub_path, self.ref_path)
