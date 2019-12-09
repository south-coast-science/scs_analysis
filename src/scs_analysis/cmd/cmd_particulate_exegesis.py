"""
Created on 26 Oct 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_core.particulate.exegesis.exegete import Exegete


# --------------------------------------------------------------------------------------------------------------------

class CmdParticulateExegesis(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        model_names = ' | '.join(Exegete.model_names())

        self.__parser = optparse.OptionParser(usage="%prog -e EXEGETE [-v] RH_PATH PMX_PATH [EXEGESIS_ROOT]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--exegete", "-e", type="string", nargs=1, action="store", default=None,
                                 dest="exegete", help="exegete model { %s }" % model_names)

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.exegete is None or self.rh_path is None or self.pmx_path is None:
            return False

        if self.exegete not in Exegete.model_names():
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
    def rh_path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def pmx_path(self):
        return self.__args[1] if len(self.__args) > 1 else None


    @property
    def exegesis_path(self):
        return self.__args[2] if len(self.__args) > 2 else Exegete.root()


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdParticulateExegesis:{exegete:%s, verbose:%s, rh_path:%s, pmx_path:%s, exegesis_path:%s}" % \
               (self.exegete, self.verbose, self.rh_path, self.pmx_path, self.exegesis_path)
