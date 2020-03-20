"""
Created on 19 Nov 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleTimezone(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -z | [-i ISO_PATH] TIMEZONE_NAME }", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--zones", "-z", action="store_true", dest="zones", default=False,
                                 help="list the available timezone names to stderr")

        self.__parser.add_option("--iso-path", "-i", type="string", nargs=1, action="store", default="rec", dest="iso",
                                 help="path for ISO 8601 datetime output (default 'rec')")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.timezone) == bool(self.__opts.zones):
            return False

        if self.iso is not None and self.timezone is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def zones(self):
        return self.__opts.zones


    @property
    def iso(self):
        return self.__opts.iso


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def timezone(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleTimezone:{zones:%s, iso:%s, verbose:%s, timezone:%s}" % \
               (self.zones, self.iso, self.verbose, self.timezone)
