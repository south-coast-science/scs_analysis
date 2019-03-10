"""
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdMultiChart(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-b] [-x POINTS] [-y MIN MAX] [-e] [-v] PATH_1 .. PATH_N",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--batch", "-b", action="store_true", dest="batch_mode", default=False,
                                 help="wait for all data before displaying chart")

        self.__parser.add_option("--x", "-x", type="int", nargs=1, action="store", default=600, dest="x",
                                 help="number of x points (default 600)")

        self.__parser.add_option("--y", "-y", type="float", nargs=2, action="store", default=(-10.0, 10.0), dest="y",
                                 help="set y-axis to min / max (default -10, 10)")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if len(self.paths) == 0:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def batch_mode(self):
        return self.__opts.batch_mode


    @property
    def x(self):
        return self.__opts.x


    @property
    def y(self):
        return self.__opts.y


    @property
    def echo(self):
        return self.__opts.echo


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def paths(self):
        return set(self.__args)


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdMultiChart:{batch_mode:%s, x:%d, y:%s, echo:%s, verbose:%s, paths:%s}" % \
                    (self.batch_mode, self.x, self.y, self.echo, self.verbose, self.paths)
