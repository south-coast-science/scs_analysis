"""
Created on 4 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdHistoChart(object):
    """
    unix command line handler
    """

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-b] [-x MIN MAX] [-c BIN_COUNT] [-p PRECISION] "
                                                    "[-o FILENAME] [-e] [-t TITLE] [-v] PATH", version=version())

        # mode...
        self.__parser.add_option("--batch", "-b", action="store_true", dest="batch_mode", default=False,
                                 help="wait for all data before displaying chart")

        self.__parser.add_option("--x", "-x", type="float", nargs=2, action="store", default=(-1.0, 1.0), dest="x",
                                 help="set x-axis to min / max (default -1, 1)")

        self.__parser.add_option("--bincount", "-c", type="int", action="store", default=200, dest="bin_count",
                                 help="number of bins (default 200)")

        self.__parser.add_option("--skip-malformed", "-s", action="store_true", dest="skip_malformed", default=False,
                                 help="ignore rows with missing path values")

        # output...
        self.__parser.add_option("--precision", "-p", type="int", action="store", default=3, dest="precision",
                                 help="precision of reported deltas (default 3)")

        self.__parser.add_option("--output", "-o", type="string", action="store", dest="outfile",
                                 help="output histogram to CSV file")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout")

        self.__parser.add_option("--title", "-t", type="string", action="store", dest="title",
                                 help="chart title")

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
    def batch_mode(self):
        return self.__opts.batch_mode


    @property
    def x(self):
        return self.__opts.x


    @property
    def bin_count(self):
        return self.__opts.bin_count


    @property
    def precision(self):
        return self.__opts.precision


    @property
    def outfile(self):
        return self.__opts.outfile


    @property
    def echo(self):
        return self.__opts.echo


    @property
    def skip_malformed(self):
        return self.__opts.skip_malformed


    @property
    def title(self):
        return self.__opts.title


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
        return "CmdHistoChart:{batch_mode:%s, x:%s, bin_count:%d, precision:%d, outfile:%s, echo:%s, " \
               "skip_malformed:%s, title:%s, verbose:%s, path:%s}" % \
                    (self.batch_mode, self.x, self.bin_count, self.precision, self.outfile, self.echo,
                     self.skip_malformed, self.title, self.verbose, self.path)
