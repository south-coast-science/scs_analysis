"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.aws.manager.configuration_finder import ConfigurationRequest


# --------------------------------------------------------------------------------------------------------------------

class CmdConfigurationMonitor(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-t TAG] [{ -o | -l [-d] }] [-i INDENT] [-v]",
                                              version="%prog 1.0")

        # filters..
        self.__parser.add_option("--tag-filter", "-t", type="string", action="store", dest="tag_filter",
                                 help="the (partial) tag of the device(s)")

        # output..
        self.__parser.add_option("--tags-only", "-o", action="store_true", dest="tags_only", default=False,
                                 help="report device tags only")

        self.__parser.add_option("--history", "-l", action="store_true", dest="history", default=False,
                                 help="report the history of one device")

        self.__parser.add_option("--diff", "-d", action="store_true", dest="diff", default=False,
                                 help="report differences only (for history)")

        self.__parser.add_option("--indent", "-i", type="int", nargs=1, action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.tags_only and self.history:
            return False

        if self.diff and not self.history:
            return False

        return True


    def response_mode(self):
        if self.tags_only:
            return ConfigurationRequest.MODE.TAGS_ONLY

        if self.history:
            return ConfigurationRequest.MODE.HISTORY

        return ConfigurationRequest.MODE.FULL


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def tag_filter(self):
        return self.__opts.tag_filter

    @property
    def tags_only(self):
        return self.__opts.tags_only


    @property
    def history(self):
        return self.__opts.history


    @property
    def diff(self):
        return self.__opts.diff


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
        return "CmdConfigurationMonitor:{tag_filter:%s, tags_only:%s, history:%s, diff:%s, indent:%s, verbose:%s}" % \
               (self.tag_filter, self.tags_only, self.history, self.diff, self.indent, self.verbose)
