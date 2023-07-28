"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import logging
import optparse

from scs_analysis import version

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.timedelta import Timedelta


# TODO: add backoff limit flag
# --------------------------------------------------------------------------------------------------------------------

class CmdAWSTopicHistory(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] { -l | -a LATEST_AT [-b BACK-OFF] | "
                                                    "-t { [[DD-]HH:]MM[:SS] | :SS } | -s START [-e END] } "
                                                    "{ -p HH:MM:SS [-m] [-x] | [-w] [-f] } [-r] [{ -v | -d }] TOPIC",
                                              version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # functions...
        self.__parser.add_option("--latest", "-l", action="store_true", dest="latest", default=False,
                                 help="the most recent document")

        self.__parser.add_option("--latest-at", "-a", type="string", action="store", dest="latest_at",
                                 help="the most recent document before ISO 8601 datetime")

        self.__parser.add_option("--back-off", "-b", type="int", action="store", dest="back_off",
                                 help="maximum look-back period (seconds)")

        self.__parser.add_option("--timedelta", "-t", type="string", action="store", dest="timedelta",
                                 help="starting days / hours / minutes / seconds ago, and ending now")

        self.__parser.add_option("--start", "-s", type="string", action="store", dest="start",
                                 help="ISO 8601 datetime START")

        self.__parser.add_option("--end", "-e", type="string", action="store", dest="end",
                                 help="ISO 8601 datetime END")

        # aggregation...
        self.__parser.add_option("--checkpoint", "-p", type="string", action="store", dest="checkpoint",
                                 help="a time specification as **:/05:00")

        self.__parser.add_option("--min-max", "-m", action="store_true", dest="min_max", default=False,
                                 help="include min and max in addition to midpoint")

        self.__parser.add_option("--exclude-remainder", "-x", action="store_true", dest="exclude_remainder",
                                 help="ignore documents after the last complete period")

        # output...
        self.__parser.add_option("--wrapper", "-w", action="store_true", dest="include_wrapper", default=False,
                                 help="include storage wrapper")

        self.__parser.add_option("--fetch-last", "-f", action="store_true", dest="fetch_last", default=False,
                                 help="fetch the last available hour of data if the requested data is unavailable")

        self.__parser.add_option("--rec-only", "-r", action="store_true", dest="rec_only", default=False,
                                 help="retrieve only the rec field")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__parser.add_option("--debug", "-d", action="store_true", dest="debug", default=False,
                                 help="report narrative and request / response to stderr")

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

        if self.back_off is not None and not self.latest_at:
            return False

        if self.include_wrapper and self.checkpoint:
            return False

        if self.rec_only and self.fetch_last:
            return False

        if self.rec_only and self.min_max:
            return False

        if self.min_max and not self.checkpoint:
            return False

        if self.exclude_remainder and not self.checkpoint:
            return False

        if self.verbose and self.debug:
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


    def log_level(self):
        if self.debug:
            return logging.DEBUG

        if self.verbose:
            return logging.INFO

        return logging.ERROR


    # ----------------------------------------------------------------------------------------------------------------
    # properties: identity...

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def latest(self):
        return self.__opts.latest


    @property
    def latest_at(self):
        return LocalizedDatetime.construct_from_iso8601(self.__opts.latest_at)


    @property
    def back_off(self):
        return self.__opts.back_off


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
    def fetch_last(self):
        return self.__opts.fetch_last


    @property
    def checkpoint(self):
        return self.__opts.checkpoint


    @property
    def include_wrapper(self):
        return self.__opts.include_wrapper


    @property
    def rec_only(self):
        return self.__opts.rec_only


    @property
    def min_max(self):
        return self.__opts.min_max


    @property
    def exclude_remainder(self):
        return self.__opts.exclude_remainder


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def debug(self):
        return self.__opts.debug


    @property
    def topic(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSTopicHistory:{credentials_name:%s, latest:%s, latest_at:%s, latest_at:%s, timedelta:%s, " \
               "start:%s, end:%s, fetch_last:%s, checkpoint:%s, include_wrapper:%s, rec_only:%s, " \
               "min_max:%s, exclude_remainder:%s, verbose:%s, debug:%s, topic:%s}" % \
                    (self.credentials_name, self.latest, self.__opts.latest_at, self.back_off, self.__opts.timedelta,
                     self.start, self.end, self.fetch_last, self.checkpoint, self.include_wrapper, self.rec_only,
                     self.min_max, self.exclude_remainder, self.verbose, self.debug, self.topic)
