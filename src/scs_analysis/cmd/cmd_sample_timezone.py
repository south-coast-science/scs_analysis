"""
Created on 19 Nov 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleTimezone(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -z | TIMEZONE_NAME }", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--zones", "-z", action="store_true", dest="zones", default=False,
                                 help="list the available timezone names to stderr")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.timezone) == bool(self.__opts.zones):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def timezone(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def zones(self):
        return self.__opts.zones


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleTimezone:{timezone:%s, zones:%s, verbose:%s}" % (self.timezone, self.zones, self.verbose)
