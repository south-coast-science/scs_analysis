"""
Created on 7 Jan 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_core.gas.exegesis.exegete_catalogue import ExegeteCatalogue


# --------------------------------------------------------------------------------------------------------------------

class CmdGasExegete(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        model_names = ' | '.join(ExegeteCatalogue.model_names())

        self.__parser = optparse.OptionParser(usage="%prog -e EXEGETE -g GAS -r RH_MIN RH_MAX RH_DELTA "
                                                    "-t T_MIN T_MAX T_DELTA [-v]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--exegete", "-e", type="string", nargs=1, action="store", default=None,
                                 dest="exegete", help="exegete model { %s }" % model_names)

        self.__parser.add_option("--gas", "-g", type="string", nargs=1, action="store", default=None,
                                 dest="gas", help="gas name")

        self.__parser.add_option("--rh", "-r", type="int", nargs=3, action="store", default=None,
                                 dest="rh", help="rH range (integer values)")

        self.__parser.add_option("--t", "-t", type="int", nargs=3, action="store", default=None,
                                 dest="t", help="temperature range (integer values)")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.exegete is None or self.gas is None or self.__opts.rh is None or self.__opts.t is None:
            return False

        if self.exegete not in ExegeteCatalogue.model_names():
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exegete(self):
        return self.__opts.exegete


    @property
    def gas(self):
        return self.__opts.gas


    @property
    def rh_min(self):
        return None if self.__opts.rh is None else self.__opts.rh[0]


    @property
    def rh_max(self):
        return None if self.__opts.rh is None else self.__opts.rh[1]


    @property
    def rh_delta(self):
        return None if self.__opts.rh is None else self.__opts.rh[2]


    @property
    def t_min(self):
        return None if self.__opts.t is None else self.__opts.t[0]


    @property
    def t_max(self):
        return None if self.__opts.t is None else self.__opts.t[1]


    @property
    def t_delta(self):
        return None if self.__opts.t is None else self.__opts.t[2]


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdGasExegete:{exegete:%s, gas:%s, rh:%s, t:%s, verbose:%s}" % \
               (self.exegete, self.gas, self.__opts.rh, self.__opts.t, self.verbose)
