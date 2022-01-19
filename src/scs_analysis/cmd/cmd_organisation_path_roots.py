"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdOrganisationPathRoots(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog  { -F -l ORG_LABEL | "
                                                    "-C -l ORG_LABEL -r PATH_ROOT | "
                                                    "-D -l ORG_LABEL -r PATH_ROOT } "
                                                    "[-i INDENT] [-v]", version="%prog 1.0")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="find the path roots for the given organisation")

        self.__parser.add_option("--Create", "-C", action="store_true", dest="create", default=False,
                                 help="create a path root for the given organisation and path")

        self.__parser.add_option("--Delete", "-D", action="store", dest="delete", default=False,
                                 help="delete the path root with the given organisation and path")

        # fields...
        self.__parser.add_option("--org-label", "-l", type="string", action="store", dest="org_label",
                                 help="the organisation label")

        self.__parser.add_option("--path-root", "-r", type="string", action="store", dest="path_root",
                                 help="the organisation path root")

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

        if self.create:
            count += 1

        if self.delete:
            count += 1

        if count != 1:
            return False

        if self.org_label is None:
            return False

        if (self.create or self.delete) and self.path_root is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

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
    def indent(self):
        return self.__opts.indent


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdOrganisationPathRoots:{find:%s, create:%s, delete:%s, org_label:%s, path_root:%s, " \
               "indent:%s, verbose:%s}" % \
               (self.find, self.__opts.create, self.__opts.delete, self.org_label, self.path_root,
                self.indent, self.verbose)
