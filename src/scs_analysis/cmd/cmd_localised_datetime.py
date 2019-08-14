"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdLocalizedDatetime(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { [-o HOURS] [-m MINUTES] [-s SECONDS] [-t TIMEZONE_NAME] | "
                                                    "-z }", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--hours", "-o", type="int", nargs=1, default=0, action="store", dest="hours",
                                 help="offset from now in hours")

        self.__parser.add_option("--minutes", "-m", type="int", nargs=1, default=0, action="store", dest="minutes",
                                 help="offset from now in minutes")

        self.__parser.add_option("--seconds", "-s", type="int", nargs=1, default=0, action="store", dest="seconds",
                                 help="offset from now in seconds")

        self.__parser.add_option("--timezone", "-t", type="string", nargs=1, action="store", dest="zone",
                                 help="present the time in the given zone")

        self.__parser.add_option("--zones", "-z", action="store_true", dest="list", default=False,
                                 help="list the available timezone names to stderr")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.list and (self.hours or self.minutes or self.seconds or self.zone):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def hours(self):
        return self.__opts.hours


    @property
    def minutes(self):
        return self.__opts.minutes


    @property
    def seconds(self):
        return self.__opts.seconds


    @property
    def zone(self):
        return self.__opts.zone


    @property
    def list(self):
        return self.__opts.list


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdLocalizedDatetime:{hours:%s, minutes:%s, seconds:%s, seconds:%s, seconds:%s, verbose:%s}" % \
               (self.hours, self.minutes, self.seconds, self.zone, self.list, self.verbose)
