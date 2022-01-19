"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# TODO: use per-field flags
# --------------------------------------------------------------------------------------------------------------------

class CmdOrganisationPathRoots(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog  { -F ORG_LABEL | -C ORG_LABEL PATH_ROOT | "
                                                    "-D ORG_LABEL PATH_ROOT } "
                                                    "[-i INDENT] [-v]", version="%prog 1.0")

        # operations...
        self.__parser.add_option("--Find", "-F", type="string", action="store", dest="find",
                                 help="find the path roots for the given organisation")

        self.__parser.add_option("--Create", "-C", type="string", nargs=2, action="store", dest="create",
                                 help="create a path root for the given organisation and path")

        self.__parser.add_option("--Delete", "-D", type="string", nargs=2, action="store", dest="delete",
                                 help="delete the path root with the given organisation and path")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", nargs=1, action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.find is not None:
            count += 1

        if self.create:
            count += 1

        if self.delete:
            count += 1

        if count != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def find(self):
        return self.__opts.find


    @property
    def create(self):
        return self.__opts.create is not None


    @property
    def create_org_label(self):
        return None if self.__opts.create is None else self.__opts.create[0]


    @property
    def create_path_root(self):
        return None if self.__opts.create is None else self.__opts.create[1]


    @property
    def delete(self):
        return self.__opts.delete is not None


    @property
    def delete_org_label(self):
        return None if self.__opts.delete is None else self.__opts.delete[0]


    @property
    def delete_path_root(self):
        return None if self.__opts.delete is None else self.__opts.delete[1]


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
        return "CmdOrganisationPathRoots:{find:%s, create:%s, delete:%s, indent:%s, verbose:%s}" % \
               (self.find, self.__opts.create, self.__opts.delete, self.indent, self.verbose)
