"""
Created on 9 May 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdOSIOMQTTControl(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -d TAG SERIAL_NUMBER -t TOPIC [-r] [-v] "
                                                    "CMD_TOKEN_1 .. CMD_TOKEN_N", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--device", "-d", type="string", nargs=2, action="store", dest="tag_serial",
                                 help="tag and serial number of target device")

        self.__parser.add_option("--topic", "-t", type="string", nargs=1, action="store", dest="topic",
                                 help="full topic path")

        # optional...
        self.__parser.add_option("--receipt", "-r", action="store_true", dest="receipt", default=False,
                                 help="wait for receipt from target device")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        return self.__opts.tag_serial and self.__opts.topic


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def device_tag(self):
        return self.__opts.tag_serial[0]


    @property
    def device_serial_number(self):
        return self.__opts.tag_serial[1]


    @property
    def topic(self):
        return self.__opts.topic


    @property
    def cmd_tokens(self):
        return self.__args


    @property
    def receipt(self):
        return self.__opts.receipt


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdOSIOMQTTControl:{tag_serial:%s, topic:%s, cmd_tokens:%s, receipt:%s, verbose:%s, args:%s}" % \
               (self.__opts.tag_serial, self.topic, self.cmd_tokens, self.receipt, self.verbose, self.args)
