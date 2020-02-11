"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_core.data.datetime import LocalizedDatetime


# --------------------------------------------------------------------------------------------------------------------

class CmdOSIOTopicHistory(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -m MINUTES | -s START [-e END] } [-p SECONDS] [-w] "
                                                    "[-v] PATH", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--minutes", "-m", type="int", nargs=1, action="store", dest="minutes",
                                 help="starting minutes ago")

        self.__parser.add_option("--start", "-s", type="string", nargs=1, action="store", dest="start",
                                 help="ISO 8601 datetime start")

        self.__parser.add_option("--end", "-e", type="string", nargs=1, action="store", dest="end",
                                 help="ISO 8601 datetime end")

        self.__parser.add_option("--pause", "-p", type="float", nargs=1, action="store", dest="pause", default=0.0,
                                 help="pause for SECONDS between retrieved batches (prevents rate limit exceeded)")

        self.__parser.add_option("--wrapping", "-w", action="store_true", dest="include_wrapping", default=False,
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
        return LocalizedDatetime.construct_from_iso8601(self.__opts.start) if self.__opts.start else None


    @property
    def end(self):
        return LocalizedDatetime.construct_from_iso8601(self.__opts.end) if self.__opts.end else None


    @property
    def pause(self):
        return self.__opts.pause

    @property
    def include_wrapping(self):
        return self.__opts.include_wrapping


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdOSIOTopicHistory:{minutes:%s, start:%s, end:%s, pause:%s, include_wrapping:%s, " \
               "verbose:%s, path:%s}" % \
                    (self.minutes, self.start, self.end, self.pause, self.include_wrapping,
                     self.verbose, self.path)
