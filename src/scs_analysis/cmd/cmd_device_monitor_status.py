"""
Created on 28 Jun 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdDeviceMonitorStatus(object):
    """unix command line handler"""

    # --------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] [-t DEVICE_TAG [-x]] "
                                                    "[-i INDENT] [-v]", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # filters...
        self.__parser.add_option("--tag-filter", "-t", type="string", action="store", dest="tag_filter",
                                 help="the (partial) tag of the device(s)")

        self.__parser.add_option("--exactly", "-x", action="store_true", dest="exact_match", default=False,
                                 help="exact match for tag")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.exact_match and self.tag_filter is None:
            return False

        if self.__args:
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
    def tag_filter(self):
        return self.__opts.tag_filter


    @property
    def exact_match(self):
        return self.__opts.exact_match



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
        return "CmdDeviceMonitorStatus:{credentials_name:%s, tag_filter:%s, exact_match:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.tag_filter, self.exact_match, self.indent, self.verbose)
