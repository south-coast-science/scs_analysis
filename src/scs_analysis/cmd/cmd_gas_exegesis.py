"""
Created on 4 Feb 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_core.sample.sample import Sample
from scs_core.gas.exegesis.exegete_catalogue import ExegeteCatalogue


# --------------------------------------------------------------------------------------------------------------------

class CmdGasExegesis(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        model_names = ' | '.join(ExegeteCatalogue.model_names())

        self.__parser = optparse.OptionParser(usage="%prog -e EXEGETE [-v] T_PATH RH_PATH REPORT_SUB_PATH "
                                                    "[EXEGESIS_SUB_PATH]", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--exegete", "-e", type="string", nargs=1, action="store", default=None,
                                 dest="exegete", help="exegete model { %s }" % model_names)

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.exegete is None or self.rh_path is None or self.t_path is None or self.report_path is None:
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
    def t_path(self):
        return self.__args[1] if len(self.__args) > 1 else None


    @property
    def rh_path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def report_path(self):
        return self.__args[2] if len(self.__args) > 2 else None


    @property
    def exegesis_path(self):
        return self.__args[3] if len(self.__args) > 3 else Sample.EXEGESIS_TAG


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdGasExegesis:{exegete:%s, verbose:%s, t_path:%s, rh_path:%s, report_path:%s, exegesis_path:%s}" % \
               (self.exegete, self.verbose, self.t_path, self.rh_path, self.report_path, self.exegesis_path)
