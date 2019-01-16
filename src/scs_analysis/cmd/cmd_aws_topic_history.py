"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse
import re

from scs_core.data.localized_datetime import LocalizedDatetime


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSTopicHistory(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -l | -t [HH:]MM | -s START [-e END] } [-w] [-v] TOPIC",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--latest", "-l", action="store_true", dest="latest", default=False,
                                 help="the most recent document only")

        self.__parser.add_option("--timedelta", "-t", type="string", nargs=1, action="store", dest="timedelta",
                                 help="starting hours / minutes ago and ending now")

        self.__parser.add_option("--start", "-s", type="string", nargs=1, action="store", dest="start",
                                 help="localised datetime start")

        self.__parser.add_option("--end", "-e", type="string", nargs=1, action="store", dest="end",
                                 help="localised datetime end")

        self.__parser.add_option("--wrapper", "-w", action="store_true", dest="include_wrapper", default=False,
                                 help="include storage wrapper")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.topic is None:
            return False

        if self.__opts.timedelta is not None and self.minutes is None:
            return False

        count = 0

        if self.latest:
            count += 1

        if self.minutes is not None:
            count += 1

        if self.start is not None:
            count += 1

        if count != 1:
            return False

        if self.__opts.start is not None and LocalizedDatetime.construct_from_iso8601(self.__opts.start) is None:
            return False

        if self.__opts.end is not None and LocalizedDatetime.construct_from_iso8601(self.__opts.end) is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def use_offset(self):
        return self.__opts.timedelta is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def latest(self):
        return self.__opts.latest


    @property
    def minutes(self):
        match = re.match('((\d+):)?(\d+)', self.__opts.timedelta)

        if match is None:
            return None

        fields = match.groups()

        hours = 0 if fields[1] is None else int(fields[1])
        minutes = (hours * 60) + int(fields[2])

        return minutes


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
    def topic(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSTopicHistory:{latest:%s, timedelta:%s, start:%s, end:%s, include_wrapper:%s, " \
               "verbose:%s, topic:%s}" % \
                    (self.latest, self.__opts.timedelta, self.start, self.end, self.include_wrapper,
                     self.verbose, self.topic)
