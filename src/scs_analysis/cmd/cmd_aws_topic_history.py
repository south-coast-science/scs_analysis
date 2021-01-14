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
        self.__parser = optparse.OptionParser(usage="%prog { -l | -a LATEST_AT | -t { [[DD-]HH:]MM[:SS] | :SS } | "
                                                    "-s START [-e END] } { [-c HH:MM:SS] | [-w] [-f] } [-r] [-v] TOPIC",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--latest", "-l", action="store_true", dest="latest", default=False,
                                 help="the most recent document")

        self.__parser.add_option("--latest-at", "-a", type="string", nargs=1, action="store", dest="latest_at",
                                 help="the most recent document up to ISO 8601 datetime LATEST_AT")

        self.__parser.add_option("--timedelta", "-t", type="string", nargs=1, action="store", dest="timedelta",
                                 help="starting days / hours / minutes / seconds ago, and ending now")

        self.__parser.add_option("--start", "-s", type="string", nargs=1, action="store", dest="start",
                                 help="ISO 8601 datetime START")

        self.__parser.add_option("--end", "-e", type="string", nargs=1, action="store", dest="end",
                                 help="ISO 8601 datetime END")

        self.__parser.add_option("--checkpoint", "-c", type="string", nargs=1, action="store", dest="checkpoint",
                                 help="a time specification as **:/05:00")

        self.__parser.add_option("--rec-only", "-r", action="store_true", dest="rec_only", default=False,
                                 help="retrieve only the rec field")

        self.__parser.add_option("--fetch-last", "-f", action="store_true", dest="fetch_last", default=False,
                                 help="fetch the last available hour of data if the requested data is unavailable")

        self.__parser.add_option("--wrapper", "-w", action="store_true", dest="include_wrapper", default=False,
                                 help="include storage wrapper")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.topic is None:
            return False

        if self.__opts.start is None and self.__opts.end is not None:
            return False

        count = 0

        if self.latest:
            count += 1

        if self.__opts.latest_at is not None:
            count += 1

        if self.__opts.timedelta is not None:
            count += 1

        if self.__opts.start is not None:
            count += 1

        if count != 1:
            return False

        if self.checkpoint and self.include_wrapper:
            return False

        if self.checkpoint and self.fetch_latest:
            return False

        return True


    def is_valid_latest_at(self):
        if self.__opts.latest_at is None:
            return True

        return self.latest_at is not None


    def is_valid_timedelta(self):
        if self.__opts.timedelta is None:
            return True

        return self.timedelta is not None


    def is_valid_start(self):
        if self.__opts.start is None:
            return True

        return self.start is not None


    def is_valid_end(self):
        if self.__opts.end is None:
            return True

        return self.end is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def latest(self):
        return self.__opts.latest


    @property
    def latest_at(self):
        return LocalizedDatetime.construct_from_iso8601(self.__opts.latest_at)


    @property
    def timedelta(self):
        return Timedelta.construct_from_flag(self.__opts.timedelta)


    @property
    def start(self):
        return LocalizedDatetime.construct_from_iso8601(self.__opts.start)


    @property
    def end(self):
        return LocalizedDatetime.construct_from_iso8601(self.__opts.end)


    @property
    def include_wrapper(self):
        return self.__opts.include_wrapper


    @property
    def checkpoint(self):
        return self.__opts.checkpoint


    @property
    def rec_only(self):
        return self.__opts.rec_only


    @property
    def verbose(self):
        return self.__opts.verbose

    @property
    def fetch_latest(self):
        return self.__opts.fetch_last


    @property
    def topic(self):
        return self.__args[0] if len(self.__args) > 0 else None




    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSTopicHistory:{latest:%s, latest_at:%s, timedelta:%s, start:%s, end:%s, end:%s, " \
               "rec_only:%s, include_wrapper:%s, verbose:%s, topic:%s, fetch_last:%s}" % \
                    (self.latest, self.__opts.latest_at, self.__opts.timedelta, self.start, self.end, self.checkpoint,
                     self.rec_only, self.include_wrapper, self.verbose, self.topic, self.fetch_latest)
