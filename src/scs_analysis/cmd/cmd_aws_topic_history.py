"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.data.localized_datetime import LocalizedDatetime


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSTopicHistory(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -m MINUTES | -s START [-e END] } [-w] [-v] PATH",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--minutes", "-m", type="int", nargs=1, action="store", dest="minutes",
                                 help="starting minutes ago")

        self.__parser.add_option("--start", "-s", type="string", nargs=1, action="store", dest="start",
                                 help="localised datetime start")

        self.__parser.add_option("--end", "-e", type="string", nargs=1, action="store", dest="end",
                                 help="localised datetime end")

        self.__parser.add_option("--wrapper", "-w", action="store_true", dest="include_wrapper", default=False,
                                 help="include message wrapper")

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
    def minutes(self):
        return self.__opts.minutes


    @property
    def start(self):
        return None if self.__opts.start is None else LocalizedDatetime.construct_from_iso8601(self.__opts.start)


    @property
    def end(self):
        return None if self.__opts.end is None else LocalizedDatetime.construct_from_iso8601(self.__opts.end)


    @property
    def include_wrapper(self):
        return self.__opts.include_wrapper


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSTopicHistory:{minutes:%s, start:%s, end:%s, include_wrapper:%s, " \
               "verbose:%s, path:%s, args:%s}" % \
                    (self.minutes, self.start, self.end, self.include_wrapper,
                     self.verbose, self.path, self.args)
