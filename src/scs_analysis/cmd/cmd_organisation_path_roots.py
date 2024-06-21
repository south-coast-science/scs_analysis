"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdOrganisationPathRoots(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] { -F [-l ORG_LABEL [-m]] | "
                                                    "-C -l ORG_LABEL -r PATH_ROOT | "
                                                    "-D -l ORG_LABEL -r PATH_ROOT } "
                                                    "[-i INDENT] [-v]", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="find the path roots for the given organisation")

        self.__parser.add_option("--Create", "-C", action="store_true", dest="create", default=False,
                                 help="create a path root for the given organisation and path")

        self.__parser.add_option("--Delete", "-D", action="store_true", dest="delete", default=False,
                                 help="delete the path root with the given organisation and path")

        # fields...
        self.__parser.add_option("--org-label", "-l", type="string", action="store", dest="org_label",
                                 help="the organisation label")

        self.__parser.add_option("--path-root", "-r", type="string", action="store", dest="path_root",
                                 help="the organisation path root")

        # output...
        self.__parser.add_option("--memberships", "-m", action="store_true", dest="memberships", default=False,
                                 help="show path root's user path memberships")

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

        if not self.find and self.org_label is None:
            return False

        if self.memberships and self.org_label is None:
            return False

        if (self.create or self.delete) and self.path_root is None:
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
    def org_label(self):
        return self.__opts.org_label


    @property
    def path_root(self):
        return self.__opts.path_root


    @property
    def memberships(self):
        return self.__opts.memberships


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
        return "CmdOrganisationPathRoots:{credentials_name:%s, find:%s, create:%s, delete:%s, " \
               "org_label:%s, path_root:%s, memberships:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.find, self.__opts.create, self.__opts.delete,
                self.org_label, self.path_root, self.memberships, self.indent, self.verbose)
