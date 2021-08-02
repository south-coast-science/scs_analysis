"""
Created on 29 Jun 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.aws.manager.alert_status_finder import AlertStatusFinderRequest


# --------------------------------------------------------------------------------------------------------------------

class CmdAlertStatus(object):
    """unix command line handler"""

    __CAUSES = {'L': '<L', 'U': '>U', 'N': 'NV'}

    # --------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -l | -d [-c CAUSE] } [-i INDENT] [-v] ID",
                                              version="%prog 1.0")

        # operations...
        self.__parser.add_option("--latest", "-l", action="store_true", dest="latest", default=False,
                                 help="return latest status report only")

        self.__parser.add_option("--history", "-d", action="store_true", dest="history", default=False,
                                 help="return history of status reports")

        # filters...
        self.__parser.add_option("--cause", "-c", type="string", action="store", dest="cause",
                                 help="filter by cause { L | U | N }")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", nargs=1, action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.id is None:
            return False

        if self.latest == self.history:
            return False

        if self.latest and self.__opts.cause is not None:
            return False

        if self.__opts.cause is not None and self.__opts.cause not in self.__CAUSES:
            return False

        return True


    def response_mode(self):
        return AlertStatusFinderRequest.MODE.LATEST if self.latest else AlertStatusFinderRequest.MODE.HISTORY


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        return self.__args[0] if self.__args else None


    @property
    def latest(self):
        return self.__opts.latest


    @property
    def history(self):
        return self.__opts.history


    @property
    def cause(self):
        return None if self.__opts.cause is None else self.__CAUSES[self.__opts.cause]


    @property
    def indent(self):
        return self.__opts.indent


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAlertStatus:{id:%s, latest:%s, history:%s, cause:%s, indent:%s, verbose:%s}" % \
               (self.id, self.latest, self.history, self.__opts.cause, self.indent, self.verbose)
