"""
Created on 11 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdSingleChart(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-b] [-r] [-x POINTS] [-y MIN MAX] [-e] [-t TITLE] [-v] "
                                                    "PATH", version=version())

        # mode...
        self.__parser.add_option("--batch", "-b", action="store_true", dest="batch_mode", default=False,
                                 help="wait for all data before displaying chart")

        self.__parser.add_option("--relative", "-r", action="store_true", dest="relative", default=False,
                                 help="display relative values (first value is 0)")

        self.__parser.add_option("--x", "-x", type="int", action="store", default=600, dest="x",
                                 help="number of x points (default 600)")

        self.__parser.add_option("--y", "-y", type="float", nargs=2, action="store", default=(-10.0, 10.0), dest="y",
                                 help="set y-axis to min / max (default -10, 10)")

        self.__parser.add_option("--skip-malformed", "-s", action="store_true", dest="skip_malformed", default=False,
                                 help="ignore rows with missing path values")

        # output...
        self.__parser.add_option("--title", "-t", type="string", action="store", dest="title",
                                 help="chart title")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout")

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
    def relative(self):
        return self.__opts.relative


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
        return "CmdSingleChart:{batch_mode:%s, relative:%s, x:%d, y:%s, echo:%s, skip_malformed:%s, title:%s, " \
               "verbose:%s, path:%s}" % \
                    (self.batch_mode, self.relative, self.x, self.y, self.echo, self.skip_malformed, self.title,
                     self.verbose, self.path)
