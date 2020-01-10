"""
Created on 9 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleUnbaselinedCnc(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -a AFE_SERIAL_NUMBER [-v] REPORT_SUB_PATH",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--afe", "-a", type="string", nargs=1, action="store", dest="afe_serial_number",
                                 help="use given AFE calibration data")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.afe_serial_number is None:
            return False

        if len(self.__args) != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def afe_serial_number(self):
        return self.__opts.afe_serial_number


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def report_sub_path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleUnbaselinedCnc:{afe_serial_number:%s, verbose:%s, report_sub_path:%s}" % \
               (self.afe_serial_number, self.verbose, self.report_sub_path)
