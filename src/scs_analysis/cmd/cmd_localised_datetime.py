"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdLocalizedDatetime(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-o HOURS] [-m MINUTES] [-s SECONDS]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--hours", "-o", type="int", nargs=1, default=0, action="store", dest="hours",
                                 help="offset from now in hours")

        self.__parser.add_option("--minutes", "-m", type="int", nargs=1, default=0, action="store", dest="minutes",
                                 help="offset from now in minutes")

        self.__parser.add_option("--seconds", "-s", type="int", nargs=1, default=0, action="store", dest="seconds",
                                 help="offset from now in seconds")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


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
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CmdLocalizedDatetime:{hours:%s, minutes:%s, seconds:%s, verbose:%s, args:%s}" % \
               (self.hours, self.minutes, self.seconds, self.verbose, self.args)
