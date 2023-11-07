"""
Created on 12 Sep 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdConfigurationReport(object):
    """unix command line handler"""

    # --------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] [-v] DEVICE_TAG_1 [..DEVICE_TAG_N]",
                                              version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if not self.device_tags:
            return False

        if not self.__args:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------
    # properties: identity...

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def device_tags(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------
    # properties: output...

    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdConfigurationReport:{credentials_name:%s, device_tag:%s, verbose:%s}" % \
               (self.credentials_name, self.device_tags, self.verbose)
