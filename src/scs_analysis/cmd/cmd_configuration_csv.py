"""
Created on 7 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version

from scs_core.aws.manager.configuration.configuration_intercourse import ConfigurationRequest


# --------------------------------------------------------------------------------------------------------------------

class CmdConfigurationCSV(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] { -n | -s | -l OUTPUT_CSV | "
                                                    "{ -d | -f } [-o OUTPUT_CSV_DIR] } [-t DEVICE_TAG [-x]] "
                                                    "[-v] [NODE_1..NODE_N]", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # help...
        self.__parser.add_option("--node-names", "-n", action="store_true", dest="node_names", default=False,
                                 help="list the available nodes")

        # mode...
        self.__parser.add_option("--separate", "-s", action="store_true", dest="separate", default=False,
                                 help="retrieve latest configurations to separate CSVs (ignores NODEs)")

        self.__parser.add_option("--latest", "-l", type="string", action="store", dest="latest",
                                 help="retrieve latest configurations to single CSV")

        self.__parser.add_option("--diff-histories", "-d", action="store_true", dest="diff_histories", default=False,
                                 help="retrieve configuration history differences")

        self.__parser.add_option("--full-histories", "-f", action="store_true", dest="full_histories", default=False,
                                 help="retrieve full configuration histories")

        # filter...
        self.__parser.add_option("--device-tag", "-t", type="string", action="store", dest="device_tag",
                                 help="the device for the history report")

        self.__parser.add_option("--exactly", "-x", action="store_true", dest="exact_match", default=False,
                                 help="exact match for tag")

        # output...
        self.__parser.add_option("--output-csv-dir", "-o", type="string", action="store", dest="output_csv_dir",
                                 help="the directory in which to write histories")

        # narrative...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.node_names:
            count += 1

        if self.separate:
            count += 1

        if self.latest:
            count += 1

        if self.diff_histories:
            count += 1

        if self.full_histories:
            count += 1

        if count != 1:
            return False

        if self.device_tag is None and self.exact_match:
            return False

        return True


    def request_mode(self):
        if self.separate or self.latest:
            return ConfigurationRequest.Mode.LATEST

        if self.diff_histories:
            return ConfigurationRequest.Mode.DIFF

        if self.full_histories:
            return ConfigurationRequest.Mode.HISTORY

        return None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def node_names(self):
        return self.__opts.node_names


    @property
    def separate(self):
        return self.__opts.separate


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
    def device_tag(self):
        return self.__opts.device_tag


    @property
    def exact_match(self):
        return self.__opts.exact_match


    @property
    def output_csv_dir(self):
        return self.__opts.output_csv_dir


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
        return "CmdConfigurationCSV:{credentials_name:%s, node_names:%s, separate:%s, latest:%s, diff_histories:%s, " \
               "full_histories:%s, device_tag:%s, exact_match:%s, output_csv_dir:%s, verbose:%s, nodes:%s}" %  \
               (self.credentials_name, self.node_names, self.separate, self.latest, self.diff_histories,
                self.full_histories, self.device_tag, self.exact_match, self.output_csv_dir, self.verbose, self.nodes)
