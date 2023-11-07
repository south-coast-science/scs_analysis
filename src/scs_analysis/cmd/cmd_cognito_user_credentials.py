"""
Created on 22 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdCognitoUserCredentials(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ -l | [-c CREDENTIALS] [{ -s | -p | -t | -d }] }] "
                                                    "[-v]", version=version())

        # helpers...
        self.__parser.add_option("--list", "-l", action="store_true", dest="list", default=False,
                                 help="list the available credentials")

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be used")

        # operations...
        self.__parser.add_option("--set", "-s", action="store_true", dest="set", default=False,
                                 help="set the credentials")

        self.__parser.add_option("--update-password", "-p", action="store_true", dest="update_password", default=False,
                                 help="update the password")

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

        if self.list:
            count += 1

        if self.set:
            count += 1

        if self.update_password:
            count += 1

        if self.test:
            count += 1

        if self.delete:
            count += 1

        if count > 1:
            return False

        if self.__args:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def list(self):
        return self.__opts.list


    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def set(self):
        return self.__opts.set


    @property
    def update_password(self):
        return self.__opts.update_password


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
        return "CmdCognitoUserCredentials:{list:%s, credentials_name:%s, set:%s, update_password:%s, test:%s, " \
               "delete:%s, verbose:%s}" % \
               (self.list, self.credentials_name, self.set, self.update_password, self.test,
                self.delete, self.verbose)
