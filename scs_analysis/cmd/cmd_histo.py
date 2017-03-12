"""
Created on 4 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdHisto(object):
    """
    unix command line handler
    """

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog PATH [-b] [-x MIN MAX] [-c BINCOUNT] [-o FILENAME] [-e] [-v]",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--batch", "-b", action="store_true", dest="batch_mode", default=False,
                                 help="wait for all data before displaying chart")

        self.__parser.add_option("--x", "-x", type="float", nargs=2, action="store", default=(-1.0, 1.0), dest="x",
                                 help="set x-axis to min / max (default -1, 1)")

        self.__parser.add_option("--bincount", "-c", type="int", nargs=1, action="store", default=200, dest="bin_count",
                                 help="number of bins (default 200)")

        self.__parser.add_option("--output", "-o", type="string", nargs=1, action="store", dest="outfile",
                                 help="output histogram to CSV file")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="report samples to stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.path is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def batch_mode(self):
        return self.__opts.batch_mode


    @property
    def x(self):
        return self.__opts.x


    @property
    def bin_count(self):
        return self.__opts.bin_count


    @property
    def outfile(self):
        return self.__opts.outfile


    @property
    def echo(self):
        return self.__opts.echo


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
        return "CmdHisto:{batch_mode:%s, x:%s, bin_count:%d, outfile:%s, echo:%s, verbose:%s, args:%s}" % \
                    (self.batch_mode, self.x, self.bin_count, self.outfile, self.echo, self.verbose, self.args)
