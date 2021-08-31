"""
Created on 7 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.aws.manager.configuration_finder import ConfigurationRequest
from scs_core.estate.configuration import Configuration


# --------------------------------------------------------------------------------------------------------------------

class CmdConfigurationCSV(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -n | -l LATEST_CSV | { -d | -f } HISTORIES_CSV_DIR } [-v] "
                                                    "[NODE_1..NODE_N]", version="%prog 1.0")

        # help...
        self.__parser.add_option("--node-names", "-n", action="store_true", dest="node_names", default=False,
                                 help="list available nodes")

        # mode...
        self.__parser.add_option("--latest", "-l", type="string", action="store", dest="latest",
                                 help="retrieve latest configurations")

        self.__parser.add_option("--diff-histories", "-d", type="string", action="store", dest="diff_histories",
                                 help="retrieve configuration history differences")

        self.__parser.add_option("--full-histories", "-f", type="string", action="store", dest="full_histories",
                                 help="retrieve full configuration histories")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.node_names:
            count += 1

        if self.latest:
            count += 1

        if self.diff_histories:
            count += 1

        if self.full_histories:
            count += 1

        if count != 1:
            return False

        return True


    def request_mode(self):
        if self.latest:
            return ConfigurationRequest.MODE.LATEST

        if self.diff_histories:
            return ConfigurationRequest.MODE.DIFF

        if self.full_histories:
            return ConfigurationRequest.MODE.HISTORY

        return None


    @property
    def histories(self):
        if self.diff_histories:
            return self.diff_histories

        if self.full_histories:
            return self.full_histories

        return None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def node_names(self):
        configuration = Configuration.construct_from_jdict(None, skeleton=True)
        return list(configuration.as_json().keys())


    @property
    def latest(self):
        return self.__opts.latest


    @property
    def diff_histories(self):
        return self.__opts.diff_histories


    @property
    def full_histories(self):
        return self.__opts.full_histories


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def nodes(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdConfigurationCSV:{node_names:%s, latest:%s, diff_histories:%s, full_histories:%s, " \
               "verbose:%s, nodes:%s}" %  \
               (self.__opts.node_names, self.latest, self.diff_histories, self.full_histories,
                self.verbose, self.nodes)
