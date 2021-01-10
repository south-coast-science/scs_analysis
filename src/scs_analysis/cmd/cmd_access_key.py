"""
Created on 17 Oct 2020

@author: Jade Page (jade.page@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdAccessKey(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ -s | -d }] [-v] ", version="%prog 1.0")

        # commands..
        self.__parser.add_option("--set", "-s", action="store_true", dest="set", default=False,
                                 help="set the key")

        self.__parser.add_option("--delete", "-d", action="store_true", dest="delete", default=False,
                                 help="delete the key")

        # reporting flag..
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.set and self.delete:
            return False

        return True

    # ----------------------------------------------------------------------------------------------------------------

    @property
    def set(self):
        return self.__opts.set

    @property
    def delete(self):
        return self.__opts.delete

    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)

    def __str__(self, *args, **kwargs):
        return "CmdAccessKey:{set:%s, delete:%s, verbose:%s}" % \
               (self.set, self.delete, self.verbose)
