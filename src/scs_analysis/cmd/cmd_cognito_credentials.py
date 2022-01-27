"""
Created on 22 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdCognitoCredentials(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] [{ -s | -t | -d }] [-v]",
                                              version="%prog 1.0")

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--set", "-s", action="store_true", dest="set", default=False,
                                 help="set the credentials")

        self.__parser.add_option("--test", "-t", action="store_true", dest="test", default=False,
                                 help="test the credentials")

        self.__parser.add_option("--delete", "-d", action="store_true", dest="delete", default=False,
                                 help="delete the credentials")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.set:
            count += 1

        if self.test:
            count += 1

        if self.delete:
            count += 1

        if count > 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def set(self):
        return self.__opts.set


    @property
    def test(self):
        return self.__opts.test


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
        return "CmdCognitoCredentials:{credentials_name:%s, set:%s, test:%s, delete:%s, verbose:%s}" % \
               (self.credentials_name, self.set, self.test, self.delete, self.verbose)
