"""
Created on 17 Apr 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdDeviceController(object):
    """unix message line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] -t DEVICE_TAG [-m CMD_TOKENS [-w]] "
                                                    "[-i INDENT] [-v]", version="%prog 1.0")

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # target...
        self.__parser.add_option("--device-tag", "-t", type="string", action="store", dest="device_tag",
                                 help="the device tag")

        # mode...
        self.__parser.add_option("--message", "-m", type="string", nargs=1, action="store", dest="message",
                                 help="send the given command line string")

        # output...
        self.__parser.add_option("--wrapper", "-w", action="store_true", dest="wrapper", default=False,
                                 help="report message wrapper")

        self.__parser.add_option("--indent", "-i", type="int", nargs=1, action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.message is not None and len(self.message) < 1:
            return False

        if self.wrapper and not self.message:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def device_tag(self):
        return self.__opts.device_tag


    @property
    def message(self):
        return self.__opts.message


    @property
    def wrapper(self):
        return self.__opts.wrapper


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
        return "CmdDeviceController:{credentials_name:%s, device_tag:%s, message:%s, wrapper:%s, " \
               "indent:%s, verbose:%s}" % \
               (self.credentials_name, self.device_tag, self.message, self.wrapper,
                self.indent, self.verbose)