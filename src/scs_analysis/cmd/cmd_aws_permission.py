"""
Created on 27 Feb 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSPermission(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-v] LAMBDA", version=version())

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if not self.__args or len(self.__args) != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def lambda_function(self):
        return self.__args[0] if self.__args else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSPermission:{lambda_function:%s, verbose:%s}" % (self.lambda_function, self.verbose)
