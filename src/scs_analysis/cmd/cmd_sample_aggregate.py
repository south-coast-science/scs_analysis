"""
Created on 24 Aug 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.data.checkpoint_generator import CheckpointGenerator


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleAggregate(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-v] -c HH:MM:SS PATH_1 .. PATH_N", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--checkpoint", "-c", type="string", nargs=1, action="store", dest="checkpoint",
                                 help="a string such as **:/15:00")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.checkpoint_generator is None:
            return False

        if len(self.paths) < 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def checkpoint_generator(self):
        try:
            return CheckpointGenerator.construct(self.__opts.checkpoint)
        except ValueError:
            return None


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def paths(self):
        return self.__args


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleAggregate:{checkpoint:%s, verbose:%s, paths:%s, args:%s}" %  \
               (self.__opts.checkpoint, self.verbose, self.paths, self.args)
