"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version
from scs_core.aws.manager.configuration.configuration_intercourse import ConfigurationRequest


# --------------------------------------------------------------------------------------------------------------------

class CmdConfigurationMonitor(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] [-t TAG [-x]] { -l | -f | -d | -o } "
                                                    "[-i INDENT] [-v]", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # filters...
        self.__parser.add_option("--tag-filter", "-t", type="string", action="store", dest="tag_filter",
                                 help="the (partial) tag of the device(s)")

        self.__parser.add_option("--exactly", "-x", action="store_true", dest="exact_match", default=False,
                                 help="exact match for tag")

        # mode...
        self.__parser.add_option("--latest", "-l", action="store_true", dest="latest", default=False,
                                 help="report latest configuration for each device")

        self.__parser.add_option("--full-history", "-f", action="store_true", dest="history", default=False,
                                 help="report full configuration history")

        self.__parser.add_option("--diff-history", "-d", action="store_true", dest="diff", default=False,
                                 help="report configuration differences")

        self.__parser.add_option("--tags-only", "-o", action="store_true", dest="tags_only", default=False,
                                 help="report device tags only")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.latest:
            count += 1

        if self.history:
            count += 1

        if self.diff:
            count += 1

        if self.tags_only:
            count += 1

        if count != 1:
            return False

        if self.exact_match and self.tag_filter is None:
            return False

        if self.__args:
            return False

        return True


    def response_mode(self):
        if self.latest:
            return ConfigurationRequest.Mode.LATEST

        if self.history:
            return ConfigurationRequest.Mode.HISTORY

        if self.diff:
            return ConfigurationRequest.Mode.DIFF

        if self.tags_only:
            return ConfigurationRequest.Mode.TAGS_ONLY

        return None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def tag_filter(self):
        return self.__opts.tag_filter


    @property
    def exact_match(self):
        return self.__opts.exact_match


    @property
    def latest(self):
        return self.__opts.latest


    @property
    def history(self):
        return self.__opts.history


    @property
    def diff(self):
        return self.__opts.diff


    @property
    def tags_only(self):
        return self.__opts.tags_only


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
        return "CmdConfigurationMonitor:{credentials_name:%s, tag_filter:%s, exact_match:%s, latest:%s, history:%s, " \
               "diff:%s, tags_only:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.tag_filter, self.exact_match, self.latest, self.history,
                self.diff, self.tags_only, self.indent, self.verbose)
