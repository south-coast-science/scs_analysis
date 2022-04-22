"""
Created on 24 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdCognitoDevices(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog  [-c CREDENTIALS] "
                                                    "{ -F [-t TAG] "
                                                    "| -C TAG SHARED_SECRET "
                                                    "| -U TAG SHARED_SECRET "
                                                    "| -D TAG } "
                                                    "[-i INDENT] [-v]",
                                              version="%prog 1.0")

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="list the devices visible to me")

        self.__parser.add_option("--Create", "-C", type="string", action="store", nargs=2, dest="create",
                                 help="create a device")

        self.__parser.add_option("--Update", "-U", type="string", action="store", nargs=2, dest="update",
                                 help="update the device")

        self.__parser.add_option("--Delete", "-D", type="string", action="store", nargs=1, dest="delete",
                                 help="delete the device (superuser only)")

        # filters...
        self.__parser.add_option("--tag", "-t", type="string", action="store", dest="tag",
                                 help="filter by device tag")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", nargs=1, action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.find:
            count += 1

        if self.create is not None:
            count += 1

        if self.update is not None:
            count += 1

        if self.delete is not None:
            count += 1

        if count != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def find(self):
        return self.__opts.find


    @property
    def create(self):
        return self.__opts.create


    @property
    def update(self):
        return self.__opts.update


    @property
    def delete(self):
        return self.__opts.delete


    @property
    def tag(self):
        return self.__opts.tag


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
        return "CmdCognitoDevices:{credentials_name:%s, find:%s, create:%s, update:%s, delete:%s, " \
               "tag:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.find, self.create, self.update, self.delete,
                self.tag, self.indent, self.verbose)
