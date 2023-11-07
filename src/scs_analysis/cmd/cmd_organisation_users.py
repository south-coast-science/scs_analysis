"""
Created on 18 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdOrganisationUsers(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog  [-c CREDENTIALS] { -F [{ -e EMAIL | -l ORG_LABEL }] | "
                                                    "-R -e EMAIL -l ORG_LABEL | "
                                                    "-C -e EMAIL -l ORG_LABEL -o { 0 | 1 } -d { 0 | 1 } | "
                                                    "-U -e EMAIL -l ORG_LABEL [-o { 0 | 1 }] [-d { 0 | 1 }] "
                                                    "[-s { 0 | 1 }] | "
                                                    "-D -e EMAIL -l ORG_LABEL } "
                                                    "[-i INDENT] [-v]", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="find users for the given username or organisation")

        self.__parser.add_option("--Retrieve", "-R", action="store_true", dest="retrieve", default=False,
                                 help="retrieve the user for the given username and organisation")

        self.__parser.add_option("--Create", "-C", action="store_true", dest="create", default=False,
                                 help="create a user")

        self.__parser.add_option("--Update", "-U", action="store_true", dest="update", default=False,
                                 help="Update the user")

        self.__parser.add_option("--Delete", "-D", action="store_true", dest="delete", default=False,
                                 help="delete the user for the given username and organisation")

        # fields...
        self.__parser.add_option("--email", "-e", type="string", action="store", dest="email",
                                 help="the user's email address (exact match)")

        self.__parser.add_option("--org-label", "-l", type="string", action="store", dest="org_label",
                                 help="the organisation label")

        self.__parser.add_option("--org-admin", "-o", type="int", action="store", dest="org_admin",
                                 help="the organisation administrator status")

        self.__parser.add_option("--device-admin", "-d", type="int", action="store", dest="device_admin",
                                 help="the device administrator status")

        self.__parser.add_option("--suspended", "-s", type="int", action="store", dest="suspended",
                                 help="the suspended status")

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

        if self.retrieve:
            count += 1

        if self.create:
            count += 1

        if self.update:
            count += 1

        if self.delete:
            count += 1

        if count != 1:
            return False

        if self.org_admin is not None and self.org_admin != 0 and self.org_admin != 1:
            return False

        if self.device_admin is not None and self.device_admin != 0 and self.device_admin != 1:
            return False

        if self.suspended is not None and self.suspended != 0 and self.suspended != 1:
            return False

        if self.find and bool(self.email) and bool(self.org_label):
            return False

        if (self.retrieve or self.create or self.update or self.delete) and \
                (self.email is None or self.org_label is None):
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
    def retrieve(self):
        return self.__opts.retrieve


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
    def email(self):
        return self.__opts.email


    @property
    def org_label(self):
        return self.__opts.org_label


    @property
    def org_admin(self):
        return self.__opts.org_admin


    @property
    def device_admin(self):
        return self.__opts.device_admin


    @property
    def suspended(self):
        return self.__opts.suspended


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
        return "CmdOrganisationUsers:{credentials_name:%s, find:%s, create:%s, update:%s, delete:%s, " \
               "email:%s, org_label:%s, org_admin:%s, device_admin:%s, suspended:%s, " \
               "indent:%s, verbose:%s}" % \
               (self.credentials_name, self.find, self.create, self.update, self.delete,
                self.email, self.org_label, self.__opts.org_admin, self.__opts.device_admin, self.__opts.suspended,
                self.indent, self.verbose)
