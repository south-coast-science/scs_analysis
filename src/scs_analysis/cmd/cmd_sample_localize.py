"""
Created on 8 Aug 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleLocalize(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -z | -t TIMEZONE_NAME [-i ISO_PATH] [-v]",
                                              version=version())

        # helper...
        self.__parser.add_option("--zones", "-z", action="store_true", dest="zones", default=False,
                                 help="list the available timezone names to stderr")

        # formats...
        self.__parser.add_option("--timezone", "-t", type="string", action="store",
                                 dest="timezone", help="timezone for localization")

        self.__parser.add_option("--iso-path", "-i", type="string", action="store", default="rec", dest="iso",
                                 help="path for ISO 8601 datetime input (default 'rec')")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.zones) == bool(self.timezone):
            return False

        if self.__args:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def zones(self):
        return self.__opts.zones


    @property
    def timezone(self):
        return self.__opts.timezone


    @property
    def iso(self):
        return self.__opts.iso


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleLocalize:{zones:%s, timezone:%s, iso:%s, verbose:%s}" % \
               (self.zones, self.timezone, self.iso, self.verbose)
