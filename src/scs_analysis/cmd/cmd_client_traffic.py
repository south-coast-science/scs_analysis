"""
Created on 29 Jun 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdClientTraffic(object):
    """unix command line handler"""

    # --------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] [-e ENDPOINT] "
                                                    "{ -u | -o [-s] } -p PERIOD [-a] "
                                                    "[-i INDENT] [-v] CLIENT_1 [..CLIENT_N]", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # filters...
        self.__parser.add_option("--endpoint", "-e", type="string", action="store", dest="endpoint",
                                 help="a specific endpoint")

        self.__parser.add_option("--users", "-u", action="store_true", dest="user", default=False,
                                 help="a specific user")

        self.__parser.add_option("--organisations", "-o", action="store_true", dest="organisation", default=False,
                                 help="a specific organisation")

        self.__parser.add_option("--separate", "-s", action="store_true", dest="separate", default=False,
                                 help="report on each member individually")

        self.__parser.add_option("--period", "-p", type="string", action="store", dest="period",
                                 help="reporting period")

        self.__parser.add_option("--aggregate", "-a", action="store_true", dest="aggregate", default=False,
                                 help="aggregate data for the period")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.user) == bool(self.organisation):
            return False

        if self.period is None:
            return False

        if not self.clients:
            return False

        if self.separate and not self.organisation:
            return False

        if self.separate and len(self.clients) > 1:
            return False

        if not self.__args:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------
    # properties: identity...

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    # ----------------------------------------------------------------------------------------------------------------
    # properties: filters...

    @property
    def endpoint(self):
        return self.__opts.endpoint


    @property
    def user(self):
        return self.__opts.user


    @property
    def organisation(self):
        return self.__opts.organisation


    @property
    def separate(self):
        return self.__opts.separate


    @property
    def period(self):
        return self.__opts.period


    @property
    def aggregate(self):
        return self.__opts.aggregate


    @property
    def clients(self):
        return self.__args


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
        return "CmdClientTraffic:{credentials_name:%s, endpoint:%s, user:%s, organisation:%s, separate:%s, " \
               "period:%s, aggregate:%s, indent:%s, verbose:%s, clients:%s}" % \
               (self.credentials_name, self.endpoint, self.user, self.organisation, self.separate,
                self.period, self.aggregate, self.indent, self.verbose, self.clients)
