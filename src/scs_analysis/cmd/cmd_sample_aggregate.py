"""
Created on 24 Oct 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleAggregate(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -c HH:MM:SS [-m] [-f] [-i ISO] [-v] [PATH_1 .. PATH_N]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--checkpoint", "-c", type="string", nargs=1, action="store", dest="checkpoint",
                                 help="a time specification as **:/5:00")

        # optional...
        self.__parser.add_option("--min-max", "-m", action="store_true", dest="min_max", default=False,
                                 help="report min and max in addition to midpoint")

        self.__parser.add_option("--fill", "-f", action="store_true", dest="fill", default=False,
                                 help="fill output with checkpoints missing from input")

        self.__parser.add_option("--iso-path", "-i", type="string", nargs=1, action="store", default="rec", dest="iso",
                                 help="path for ISO 8601 datetime field (default 'rec')")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.checkpoint is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def checkpoint(self):
        return self.__opts.checkpoint


    @property
    def min_max(self):
        return self.__opts.min_max


    @property
    def fill(self):
        return self.__opts.fill


    @property
    def iso(self):
        return self.__opts.iso


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def nodes(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleAggregate:{checkpoint:%s, min_max:%s, fill:%s, iso:%s, verbose:%s, nodes:%s}" %  \
               (self.checkpoint, self.min_max, self.fill, self.iso, self.verbose, self.nodes)
