"""
Created on 21 Jun 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdGasResponseSummary(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] [-s START] [-e END] "
                                                    "[-i INDENT] [-v] DEVICE_TAG_1 [... DEVICE_TAG_N]",
                                              version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be used")

        # input...
        self.__parser.add_option("--start", "-s", type="string", action="store", dest="start",
                                 help="start time (default 24 hours ago)")

        self.__parser.add_option("--end", "-e", type="string", action="store", dest="end",
                                 help="end time (default now)")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if len(self.__args) < 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def start(self):
        return self.__opts.start


    @property
    def end(self):
        return self.__opts.end


    @property
    def indent(self):
        return self.__opts.indent


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def device_tags(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdGasResponseSummary:{credentials_name:%s, start:%s, end:%s, indent:%s, verbose:%s, " \
                "device_tags:%s}" % \
               (self.credentials_name, self.start, self.end, self.indent, self.verbose,
                self.device_tags)
