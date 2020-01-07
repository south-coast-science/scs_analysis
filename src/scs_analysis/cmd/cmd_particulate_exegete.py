"""
Created on 7 Jan 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_core.particulate.exegesis.exegete_catalogue import ExegeteCatalogue


# --------------------------------------------------------------------------------------------------------------------

class CmdParticulateExegete(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        model_names = ' | '.join(ExegeteCatalogue.model_names())

        self.__parser = optparse.OptionParser(usage="%prog -e EXEGETE -r RH_MIN RH_MAX RH_DELTA [-v]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--exegete", "-e", type="string", nargs=1, action="store", default=None,
                                 dest="exegete", help="exegete model { %s }" % model_names)

        self.__parser.add_option("--rH", "-r", type="int", nargs=3, action="store", default=None,
                                 dest="rh", help="rH range (integer values)")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.exegete is None or self.__opts.rh is None:
            return False

        if self.exegete not in ExegeteCatalogue.model_names():
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exegete(self):
        return self.__opts.exegete


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def rh_min(self):
        return None if self.__opts.rh is None else self.__opts.rh[0]


    @property
    def rh_max(self):
        return None if self.__opts.rh is None else self.__opts.rh[1]


    @property
    def rh_delta(self):
        return None if self.__opts.rh is None else self.__opts.rh[2]


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdParticulateExegete:{exegete:%s, verbose:%s, rh_min:%s, rh_max:%s, rh_delta:%s}" % \
               (self.exegete, self.verbose, self.rh_min, self.rh_max, self.rh_delta)
