"""
Created on 19 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdOSIOClientAuth(object):
    """
    unix command line handler
    """

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-u USER_ID] [-d DESCRIPTION] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--user", "-u", type="string", nargs=1, action="store", dest="user_id",
                                 help="set user-id (only if device has not yet been registered)")

        self.__parser.add_option("--desc", "-d", type="string", nargs=1, action="store", dest="description",
                                 help="set optional device description")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_complete(self):
        if self.user_id is None:
            return False

        return True


    def set(self):
        if self.__opts.user_id is None and self.__opts.description is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def user_id(self):
        return self.__opts.user_id


    @property
    def description(self):
        return self.__opts.description


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdOSIOClientAuth:{user_id:%s, description:%s, verbose:%s}" % \
               (self.user_id, self.description, self.verbose)
