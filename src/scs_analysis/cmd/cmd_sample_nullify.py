"""
Created on 4 Sep 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleNullify(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -t TARGET_PATH -s SOURCE_PATH [-l LOWER] [-u UPPER]"
                                                    " [-v]", version=version())

        # input...
        self.__parser.add_option("--target", "-t", type="string", action="store", dest="target",
                                 help="field to be nullified")

        self.__parser.add_option("--source", "-s", type="string", action="store", dest="source",
                                 help="field providing the test value")

        # operation...
        self.__parser.add_option("--lower", "-l", type="float", action="store", dest="lower",
                                 help="lower bound")

        self.__parser.add_option("--upper", "-u", type="float", action="store", dest="upper",
                                 help="upper bound")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.target is None or self.source is None:
            return False

        if self.lower is not None and self.upper is not None and self.upper <= self.lower:
            return False

        if self.__args:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def target(self):
        return self.__opts.target


    @property
    def source(self):
        return self.__opts.source


    @property
    def lower(self):
        return self.__opts.lower


    @property
    def upper(self):
        return self.__opts.upper


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleNullify:{target:%s, source:%s, lower:%s, upper:%s, verbose:%s}" % \
               (self.target, self.source, self.lower, self.upper, self.verbose)
