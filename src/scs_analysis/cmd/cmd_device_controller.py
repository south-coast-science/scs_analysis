"""
Created on 17 Apr 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdDeviceController(object):
    """unix message line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] -t DEVICE_TAG "
                                                    "[{ [-w] [-i INDENT] | [-s] -m CMD_TOKENS }]] [-v] ",
                                              version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        self.__parser.add_option("--device-tag", "-t", type="string", action="store", dest="device_tag",
                                 help="the device tag")

        # mode...
        self.__parser.add_option("--message", "-m", type="string", action="store", dest="message",
                                 help="send the given command(s)")

        # output...
        self.__parser.add_option("--wrapper", "-w", action="store_true", dest="wrapper", default=False,
                                 help="report message wrapper")

        self.__parser.add_option("--std", "-s", action="store_true", dest="std", default=False,
                                 help="write to stderr and stdout")

        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.std and (self.indent is not None or self.wrapper):
            return False

        if (self.wrapper or self.indent or self.std) and not self.message:
            return False

        if self.__args:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------
    # properties: identity

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def device_tag(self):
        return self.__opts.device_tag


    # ----------------------------------------------------------------------------------------------------------------
    # properties: mode

    @property
    def message(self):
        return self.__opts.message


    # ----------------------------------------------------------------------------------------------------------------
    # properties: output

    @property
    def wrapper(self):
        return self.__opts.wrapper


    @property
    def std(self):
        return self.__opts.std


    @property
    def indent(self):
        return self.__opts.indent


    @property
    def commands(self):
        return self.__args


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdDeviceController:{credentials_name:%s, device_tag:%s, message:%s, wrapper:%s, std:%s, " \
               "indent:%s, verbose:%s}" % \
               (self.credentials_name, self.device_tag, self.message, self.wrapper, self.std,
                self.indent, self.verbose)
