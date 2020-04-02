"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.timedelta import Timedelta


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSTopicHistory(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -l | -t { [[DD-]HH:]MM[:SS] | :SS } | -s START [-e END] } "
                                                    "[-r] [-w] [-v] TOPIC", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--latest", "-l", action="store_true", dest="latest", default=False,
                                 help="the most recent document only")

        self.__parser.add_option("--timedelta", "-t", type="string", nargs=1, action="store", dest="timedelta",
                                 help="starting days / hours / minutes / seconds ago, and ending now")

        self.__parser.add_option("--start", "-s", type="string", nargs=1, action="store", dest="start",
                                 help="ISO 8601 datetime start")

        self.__parser.add_option("--end", "-e", type="string", nargs=1, action="store", dest="end",
                                 help="ISO 8601 datetime end")

        self.__parser.add_option("--rec-only", "-r", action="store_true", dest="rec_only", default=False,
                                 help="retrieve only the rec field")

        self.__parser.add_option("--wrapper", "-w", action="store_true", dest="include_wrapper", default=False,
                                 help="include storage wrapper")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.topic is None:
            return False

        if self.__opts.timedelta is not None and self.timedelta is None:
            return False

        count = 0

        if self.latest:
            count += 1

        if self.timedelta is not None:
            count += 1

        if self.start is not None:
            count += 1

        if count != 1:
            return False

        return True


    def is_valid_start(self):
        if self.__opts.start is None:
            return True

        return LocalizedDatetime.construct_from_iso8601(self.__opts.start) is not None


    def is_valid_end(self):
        if self.__opts.end is None:
            return True

        return LocalizedDatetime.construct_from_iso8601(self.__opts.end) is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def latest(self):
        return self.__opts.latest


    @property
    def timedelta(self):
        return Timedelta.construct_from_flag(self.__opts.timedelta)


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
    def rec_only(self):
        return self.__opts.rec_only


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def topic(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSTopicHistory:{latest:%s, timedelta:%s, start:%s, end:%s, rec_only:%s, include_wrapper:%s, " \
               "verbose:%s, topic:%s}" % \
                    (self.latest, self.timedelta, self.start, self.end, self.rec_only, self.include_wrapper,
                     self.verbose, self.topic)
