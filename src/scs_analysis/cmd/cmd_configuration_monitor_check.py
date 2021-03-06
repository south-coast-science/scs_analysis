"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.aws.manager.configuration_check_finder import ConfigurationCheckRequest

from scs_core.estate.configuration_check import ConfigurationCheck


# --------------------------------------------------------------------------------------------------------------------

class CmdConfigurationMonitorCheck(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        codes = ' | '.join(ConfigurationCheck.result_codes())

        self.__parser = optparse.OptionParser(usage="%prog [-t TAG] [-r RESULT] [-o] [-i INDENT] [-v]",
                                              version="%prog 1.0")

        # filters..
        self.__parser.add_option("--tag-filter", "-t", type="string", action="store", dest="tag_filter",
                                 help="the (partial) tag of the device(s)")

        self.__parser.add_option("--result", "-r", type="string", nargs=1, action="store", dest="result_code",
                                 help="match the result { %s }" % codes)

        # output..
        self.__parser.add_option("--tags-only", "-o", action="store_true", dest="tags_only", default=False,
                                 help="report device tags only")

        self.__parser.add_option("--indent", "-i", type="int", nargs=1, action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.result_code and self.result_code not in ConfigurationCheck.result_codes():
            return False

        return True


    def result(self):
        return ConfigurationCheck.result_string(self.result_code)


    def response_mode(self):
        return ConfigurationCheckRequest.MODE.TAGS_ONLY if self.tags_only else ConfigurationCheckRequest.MODE.FULL


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def tag_filter(self):
        return self.__opts.tag_filter


    @property
    def result_code(self):
        return self.__opts.result_code


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
        return "CmdConfigurationMonitorCheck:{tag_filter:%s, result_code:%s, tags_only:%s, indent:%s, verbose:%s}" % \
               (self.tag_filter, self.result_code, self.tags_only, self.indent, self.verbose)
