"""
Created on 15 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version
from scs_core.gas.gas import Gas


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleGasConcentration(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-v] GAS DENSITY_PATH T_PATH [{P_PATH | -p PRESSURE}]",
                                              version=version())

        # mode...
        self.__parser.add_option("--pressure", "-p", type="float", action="store", dest="pressure",
                                 default=Gas.STP_PRESSURE, help="assume constant atmospheric pressure in kPA "
                                                                "(default %s)" % Gas.STP_PRESSURE)

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if len(self.__args) < 3:
            return False

        if self.pressure is not None and self.p_path is not None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def pressure(self):
        return self.__opts.pressure


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def gas(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def density_path(self):
        return self.__args[1] if len(self.__args) > 1 else None


    @property
    def t_path(self):
        return self.__args[2] if len(self.__args) > 2 else None


    @property
    def p_path(self):
        return self.__args[3] if len(self.__args) > 3 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleGasConcentration:{pressure:%s, verbose:%s, gas:%s, density_path:%s, t_path:%s, p_path:%s}" % \
               (self.pressure, self.verbose, self.gas, self.density_path, self.t_path, self.p_path)
