"""
Created on 24 Oct 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.data.checkpoint_generator import CheckpointGenerator
from scs_core.data.topic import Topic


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleAggregate(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-m] [-v] -c HH:MM:SS PATH_1 .. PATH_N",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--min-max", "-m", action="store_true", dest="min_max", default=False,
                                 help="report min and max in addition to midpoint")

        self.__parser.add_option("--checkpoint", "-c", type="string", nargs=1, action="store", dest="checkpoint",
                                 help="a time specification as **:/5:00")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.checkpoint_generator is None:
            return False

        if self.topics is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def checkpoint_generator(self):
        try:
            return CheckpointGenerator.construct(self.__opts.checkpoint)
        except (AttributeError, ValueError):
            return None


    @property
    def topics(self):
        if len(self.__args) == 0:
            return None

        try:
            return [Topic(path) for path in self.args]

        except ValueError:
            return None


    @property
    def min_max(self):
        return self.__opts.min_max


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleAggregate:{checkpoint:%s, min_max:%s, verbose:%s, topics:%s, args:%s}" %  \
               (self.__opts.checkpoint, self.min_max, self.verbose, self.topics, self.args)
