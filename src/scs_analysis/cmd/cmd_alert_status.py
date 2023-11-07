"""
Created on 29 Jun 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version
from scs_core.aws.monitor.alert.alert_status_intercourse import AlertStatusFindRequest


# --------------------------------------------------------------------------------------------------------------------

class CmdAlertStatus(object):
    """unix command line handler"""

    __CAUSES = {'L': '<L', 'U': '>U', 'N': 'NV', 'OK': 'OK'}

    # --------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        causes = ' | '.join(self.__CAUSES)

        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] { -F { -l | -d [-a CAUSE] } | -D } "
                                                    "[-i INDENT] [-v] ID", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--find", "-F", action="store_true", dest="find", default=False,
                                 help="find alert status reports")

        self.__parser.add_option("--delete", "-D", action="store_true", dest="delete", default=False,
                                 help="delete the alert status history")

        # filters...
        self.__parser.add_option("--latest", "-l", action="store_true", dest="latest", default=False,
                                 help="find latest status report only")

        self.__parser.add_option("--history", "-d", action="store_true", dest="history", default=False,
                                 help="find history of status reports")

        self.__parser.add_option("--cause", "-a", type="string", action="store", dest="cause",
                                 help="filter history by cause { %s }" % causes)

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.id is None:
            return False

        if self.find == self.delete:
            return False

        if self.find and self.latest == self.history:
            return False

        if not self.find and (self.latest or self.history):
            return False

        if self.latest and self.__opts.cause is not None:
            return False

        if self.__opts.cause is not None and self.__opts.cause not in self.__CAUSES:
            return False

        if not self.__args or len(self.__args) != 1:
            return False

        return True


    def response_mode(self):
        return AlertStatusFindRequest.Mode.LATEST if self.latest else AlertStatusFindRequest.Mode.HISTORY


    # ----------------------------------------------------------------------------------------------------------------
    # properties: identity...

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def id(self):
        return self.__args[0] if self.__args else None


    # ----------------------------------------------------------------------------------------------------------------
    # properties: operations...

    @property
    def find(self):
        return self.__opts.find


    @property
    def delete(self):
        return self.__opts.delete


    # ----------------------------------------------------------------------------------------------------------------
    # properties: filters...

    @property
    def latest(self):
        return self.__opts.latest


    @property
    def history(self):
        return self.__opts.history


    @property
    def cause(self):
        return None if self.__opts.cause is None else self.__CAUSES[self.__opts.cause]


    # ----------------------------------------------------------------------------------------------------------------
    # properties: output...

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
        return "CmdAlertStatus:{credentials_name:%s, id:%s, find:%s, delete:%s, latest:%s, history:%s, cause:%s, " \
               "indent:%s, verbose:%s}" % \
               (self.credentials_name, self.id, self.find, self.delete, self.latest, self.history, self.__opts.cause,
                self.indent, self.verbose)
