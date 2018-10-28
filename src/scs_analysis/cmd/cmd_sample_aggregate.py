"""
Created on 24 Oct 2018

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
        self.__parser = optparse.OptionParser(usage="%prog [-v] -c HH:MM:SS PATH_1 PRECISION_1 .. PATH_N PRECISION_N",
                                              version="%prog 1.0")

        # optional...
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
    def verbose(self):
        return self.__opts.verbose


    @property
    def topics(self):
        if len(self.__args) == 0 or len(self.args) % 2 == 1:
            return None

        try:
            topics = {}
            for i in range(0, len(self.args), 2):
                topics[self.args[i]] = int(self.args[i + 1])

            return topics

        except ValueError:
            return None


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleAggregate:{checkpoint:%s, verbose:%s, topics:%s, args:%s}" %  \
               (self.__opts.checkpoint, self.verbose, self.topics, self.args)
