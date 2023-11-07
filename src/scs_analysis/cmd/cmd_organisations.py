"""
Created on 10 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdOrganisations(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] { -F [-l LABEL] [-m] | "
                                                    "-C -l LABEL -n LONG_NAME -u URL -o OWNER_EMAIL "
                                                    "[-p PARENT_LABEL] | "
                                                    "-U LABEL [-l LABEL] [-n LONG_NAME] [-u URL] [-o OWNER_EMAIL] "
                                                    "[-p PARENT_LABEL] | "
                                                    "-D LABEL } "
                                                    "[-i INDENT] [-v]", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="find the organisations I belong to")

        self.__parser.add_option("--Create", "-C", action="store_true", dest="create", default=False,
                                 help="create an organisation")

        self.__parser.add_option("--Update", "-U", type="string", action="store", dest="update",
                                 help="update the organisation with the given LABEL")

        self.__parser.add_option("--Delete", "-D", type="string", action="store", dest="delete",
                                 help="delete the organisation")

        # fields...
        self.__parser.add_option("--label", "-l", type="string", action="store", dest="label",
                                 help="the organisation label")

        self.__parser.add_option("--long-name", "-n", type="string", action="store", dest="long_name",
                                 help="the organisation long name")

        self.__parser.add_option("--url", "-u", type="string", action="store", dest="url",
                                 help="the organisation URL")

        self.__parser.add_option("--owner", "-o", type="string", action="store", dest="owner",
                                 help="the organisation owner email")

        self.__parser.add_option("--parent", "-p", type="string", action="store", dest="parent_label",
                                 help="the label of the parent organisation ('none' to remove)")

        # output...
        self.__parser.add_option("--memberships", "-m", action="store_true", dest="memberships", default=False,
                                 help="show organisation's children")

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

        if self.update is not None:
            count += 1

        if self.delete is not None:
            count += 1

        if count != 1:
            return False

        if self.create and (self.label is None or self.long_name is None or self.url is None or self.owner is None):
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
    def update(self):
        return self.__opts.update


    @property
    def delete(self):
        return self.__opts.delete


    @property
    def label(self):
        return self.__opts.label


    @property
    def long_name(self):
        return self.__opts.long_name


    @property
    def url(self):
        return self.__opts.url


    @property
    def owner(self):
        return self.__opts.owner


    @property
    def parent_label(self):
        return self.__opts.parent_label


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
        return "CmdOrganisations:{credentials_name:%s, find:%s, create:%s, update:%s, delete:%s, " \
               "label:%s, long_name:%s, url:%s, owner:%s, parent_label:%s, " \
               "memberships:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.find, self.create, self.update, self.delete,
                self.label, self.long_name, self.url, self.owner, self.parent_label,
                self.memberships, self.indent, self.verbose)
