"""
Created on 15 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleISO8601(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-v] { -z | [-i ISO_PATH] [-t TIMEZONE_NAME] "
                                                    "{ DATETIME_PATH | DATE_PATH TIME_PATH } }", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--zones", "-z", action="store_true", dest="zones", default=False,
                                 help="list the available timezone names to stderr")

        self.__parser.add_option("--timezone", "-t", type="string", nargs=1, action="store", default=None,
                                 dest="timezone", help="source timezone (default 'UTC')")

        self.__parser.add_option("--iso", "-i", type="string", nargs=1, action="store", default="rec", dest="iso",
                                 help="path for ISO 8601 datetime output (default 'rec')")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.zones:
            return True

        if len(self.__args) < 1 or len(self.__args) > 2:
            return False

        return True


    def datetime_paths(self):
        if self.uses_datetime():
            return {self.datetime_path}

        elif self.uses_date_time():
            return {self.date_path, self.time_path}

        return {}


    def uses_datetime(self):
        return len(self.__args) == 1


    def uses_date_time(self):
        return len(self.__args) == 2


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


    @property
    def datetime_path(self):
        return self.__args[0] if self.uses_datetime() else None


    @property
    def date_path(self):
        return self.__args[0] if self.uses_date_time() else None


    @property
    def time_path(self):
        return self.__args[1] if self.uses_date_time() else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleISO8601:{zones:%s, timezone:%s, iso:%s, verbose:%s, datetime_paths:%s}" % \
               (self.zones, self.timezone, self.iso, self.verbose, self.datetime_paths())
