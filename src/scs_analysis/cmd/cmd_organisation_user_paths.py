"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdOrganisationUserPaths(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog  [-c CREDENTIALS] { -F { -e EMAIL | -r PATH_ROOT } | "
                                                    "-C -e EMAIL -r PATH_ROOT -x PATH_EXTENSION | "
                                                    "-D -e EMAIL -r PATH_ROOT -x PATH_EXTENSION } "
                                                    "[-i INDENT] [-v]", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="find users for the given username or organisation")

        self.__parser.add_option("--Create", "-C", action="store_true", dest="create", default=False,
                                 help="create a user")

        self.__parser.add_option("--Delete", "-D", action="store_true", dest="delete", default=False,
                                 help="delete the user for the given username and organisation")

        # fields...
        self.__parser.add_option("--email", "-e", type="string", action="store", dest="email",
                                 help="the user's email address'")

        self.__parser.add_option("--path-root", "-r", type="string", action="store", dest="path_root",
                                 help="the organisation path root")

        self.__parser.add_option("--path-extension", "-x", type="string", action="store", dest="path_extension",
                                 help="the organisation path root")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.find:
            count += 1

        if self.create:
            count += 1

        if self.delete:
            count += 1

        if count != 1:
            return False

        if self.find:
            if self.email is None and self.path_root is None:
                return False
        else:
            if self.email is None or self.path_root is None:
                return False

        if (self.create or self.delete) and self.path_extension is None:
            return False

        if self.__args:
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
    def delete(self):
        return self.__opts.delete


    @property
    def email(self):
        return self.__opts.email


    @property
    def path_root(self):
        return self.__opts.path_root


    @property
    def path_extension(self):
        return self.__opts.path_extension


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
        return "CmdOrganisationUserPaths:{credentials_name:%s, find:%s, create:%s, delete:%s, " \
               "email:%s, path_root:%s, path_extension:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.find, self.create, self.delete,
                self.email, self.path_root, self.path_extension, self.indent, self.verbose)
