"""
Created on 17 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.data.localized_datetime import LocalizedDatetime


# --------------------------------------------------------------------------------------------------------------------

class CmdOSIOTopicRetrieve(object):
    """unix command line handler"""

    def __init__(self):
        """stuff"""
        self.__parser = optparse.OptionParser(usage="%prog PATH { -m MINUTES | -s START [-e END] } [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--minutes", "-m", type="int", nargs=1, action="store", dest="minutes",
                                 help="starting minutes ago")

        self.__parser.add_option("--start", "-s", type="string", nargs=1, action="store", dest="start",
                                 help="localised datetime start")

        self.__parser.add_option("--end", "-e", type="string", nargs=1, action="store", dest="end",
                                 help="localised datetime end")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.path is None or (self.__opts.start is None and self.minutes is None):
            return False

        if self.__opts.start is not None and LocalizedDatetime.construct_from_iso8601(self.__opts.start) is None:
            return False

        if self.__opts.end is not None and LocalizedDatetime.construct_from_iso8601(self.__opts.end) is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def use_offset(self):
        return self.minutes is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def minutes(self):
        return self.__opts.minutes


    @property
    def start(self):
        return LocalizedDatetime.construct_from_iso8601(self.__opts.start) if self.__opts.start else None


    @property
    def end(self):
        return LocalizedDatetime.construct_from_iso8601(self.__opts.end) if self.__opts.end else None


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
        return "CmdOSIOTopicRetrieve:{path:%s, minutes:%s, start:%s, end:%s, verbose:%s, args:%s}" % \
                    (self.path, self.minutes, self.start, self.end, self.verbose, self.args)
