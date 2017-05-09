"""
Created on 17 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdControlSender(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog ATTN SERIAL_NUMBER CMD_TOKEN_1 .. CMD_TOKEN_N [-v]",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        return len(self.__args) > 4


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def attn(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def serial_number(self):
        return self.__args[1] if len(self.__args) > 1 else None


    @property
    def cmd_tokens(self):
        return self.__args[2:] if len(self.__args) > 2 else None


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
        return "CmdControlSender:{attn:%s, serial_number:%s, cmd_tokens:%s, verbose:%s, args:%s}" % \
                    (self.attn, self.serial_number, self.cmd_tokens, self.verbose, self.args)
