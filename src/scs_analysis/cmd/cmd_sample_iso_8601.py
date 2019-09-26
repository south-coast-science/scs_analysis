"""
Created on 15 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleISO8601(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -z | { -o | -f DATE_FORMAT } "
                                                    "[-t TIMEZONE_NAME [-u]] [-i ISO_PATH] "
                                                    "{ DATETIME_PATH | DATE_PATH TIME_PATH } } [-v]",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--zones", "-z", action="store_true", dest="zones", default=False,
                                 help="list the available timezone names to stderr")

        self.__parser.add_option("--oad", "-o", action="store_true", dest="oad", default=False,
                                 help="datetime format is OLE Automation date")

        self.__parser.add_option("--format", "-f", type="string", nargs=1, action="store", dest="format",
                                 help="specifies format of input date string, i.e. YYYY-MM-DD")

        self.__parser.add_option("--timezone", "-t", type="string", nargs=1, action="store",
                                 dest="timezone", help="source timezone (default 'UTC')")

        self.__parser.add_option("--utc", "-u", action="store_true", dest="utc", default=False,
                                 help="shift timezone to UTC")

        self.__parser.add_option("--iso-path", "-i", type="string", nargs=1, action="store", default="rec", dest="iso",
                                 help="path for ISO 8601 datetime output (default 'rec')")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.zones:
            return True

        if self.oad:
            return True

        if self.format is None:
            return False

        if self.utc and self.timezone is None:
            return False

        if len(self.__args) < 1 or len(self.__args) > 2:
            return False

        return True


    def datetime_paths(self):
        if self.uses_datetime():
            return {self.iso, self.datetime_path}

        elif self.uses_date_time():
            return {self.iso, self.date_path, self.time_path}

        return {self.iso}


    def uses_datetime(self):
        return len(self.__args) == 1


    def uses_date_time(self):
        return len(self.__args) == 2


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def zones(self):
        return self.__opts.zones


    @property
    def oad(self):
        return self.__opts.oad


    @property
    def format(self):
        return self.__opts.format


    @property
    def timezone(self):
        return self.__opts.timezone


    @property
    def utc(self):
        return self.__opts.utc


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
        return "CmdSampleISO8601:{zones:%s, oad:%s, format:%s, timezone:%s, utc:%s, iso:%s, verbose:%s, " \
               "datetime_paths:%s}" % \
               (self.zones, self.oad, self.format, self.timezone, self.utc, self.iso, self.verbose,
                self.datetime_paths())
