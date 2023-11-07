"""
Created on 24 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdCognitoUserIdentity(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] { -C | -R | -U } [-i INDENT] [-v]",
                                              version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--Create", "-C", action="store_true", dest="create", default=False,
                                 help="create my identity")

        self.__parser.add_option("--Retrieve", "-R", action="store_true", dest="retrieve", default=False,
                                 help="retrieve my identity")

        self.__parser.add_option("--Update", "-U", action="store_true", dest="update", default=False,
                                 help="update my identity")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.create:
            count += 1

        if self.retrieve:
            count += 1

        if self.update:
            count += 1

        if count != 1:
            return False

        if self.__args:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def create(self):
        return self.__opts.create


    @property
    def retrieve(self):
        return self.__opts.retrieve


    @property
    def update(self):
        return self.__opts.update


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
        return "CmdCognitoUserIdentity:{credentials_name:%s, retrieve:%s, create:%s, update:%s, indent:%s, " \
               "verbose:%s}" % \
               (self.credentials_name, self.retrieve, self.create, self.update, self.indent,
                self.verbose)
