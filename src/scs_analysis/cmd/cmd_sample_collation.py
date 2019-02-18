"""
Created on 16 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleCollation(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -l LOWER_BOUND -u UPPER_BOUND -s STEP -f FILE_PREFIX "
                                                    "[-v] PATH", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--lower", "-l", type="float", nargs=1, action="store", default=None, dest="lower",
                                 help="lower bound")

        self.__parser.add_option("--upper", "-u", type="float", nargs=1, action="store", default=None, dest="upper",
                                 help="upper bound")

        self.__parser.add_option("--step", "-s", type="float", nargs=1, action="store", default=None, dest="step",
                                 help="step")

        self.__parser.add_option("--file", "-f", type="string", nargs=1, action="store", default=None, dest="file",
                                 help="file prefix")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.lower is None or self.upper is None or self.step is None or self.file is None or self.path is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def lower(self):
        return self.__opts.lower


    @property
    def upper(self):
        return self.__opts.upper


    @property
    def step(self):
        return self.__opts.step


    @property
    def file(self):
        return self.__opts.file


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleCollation:{lower:%s, upper:%s, step:%s, file:%s, verbose:%s, path:%s}" % \
               (self.lower, self.upper, self.step, self.file, self.verbose, self.path)
