"""
Created on 24 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.aws.security.cognito_user import CognitoUserIdentity


# --------------------------------------------------------------------------------------------------------------------

class CmdCognitoIdentity(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        confirmations = ' | '.join(CognitoUserIdentity.status_codes())

        self.__parser = optparse.OptionParser(usage="%prog  [-c CREDENTIALS] "
                                                    "{ -F [{ -e EMAIL_ADDR | -c CONFIRMATION | -s STATUS }] "
                                                    "| -C | -R | -U | -D EMAIL_ADDR } [-i INDENT] [-v]",
                                              version="%prog 1.0")

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="list the identities visible to me")

        self.__parser.add_option("--Create", "-C", action="store_true", dest="create", default=False,
                                 help="create an identity")

        self.__parser.add_option("--Retrieve", "-R", action="store_true", dest="retrieve", default=False,
                                 help="retrieve my identity")

        self.__parser.add_option("--Update", "-U", action="store_true", dest="update", default=False,
                                 help="update my identity")

        self.__parser.add_option("--Delete", "-D", type="string", action="store", dest="delete",
                                 help="delete identity (superuser only)")

        # filters...
        self.__parser.add_option("--email", "-e", type="string", action="store", dest="email",
                                 help="filter list by email address (partial match)")

        self.__parser.add_option("--confirmation", "-o", type="string", action="store", dest="confirmation",
                                 help="filter list by confirmation status { %s }" % confirmations)

        self.__parser.add_option("--status", "-s", type="int", action="store", dest="status",
                                 help="filter list by enabled status { 1 | 0 }")

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

        if self.retrieve:
            count += 1

        if self.update:
            count += 1

        if self.delete:
            count += 1

        if count != 1:
            return False

        count = 0

        if self.find_email is not None:
            count += 1

        if self.find_confirmation is not None:
            count += 1

        if self.find_status is not None:
            count += 1

        if count > 1:
            return False

        if self.find_confirmation is not None and self.find_confirmation not in CognitoUserIdentity.status_codes():
            return False

        if self.find_status is not None and self.find_status not in (0, 1):
            return None

        if self.find_email is not None and not self.find:
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
    def find_email(self):
        return self.__opts.email


    @property
    def find_confirmation(self):
        return self.__opts.confirmation


    @property
    def find_status(self):
        return None if self.__opts.status is None else bool(self.__opts.status)


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
    def delete(self):
        return self.__opts.delete is not None


    @property
    def delete_email(self):
        return self.__opts.delete


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
        return "CmdCognitoIdentity:{credentials_name:%s, find:%s, find_email:%s, find_confirmation:%s, " \
               "find_status:%s, retrieve:%s, create:%s, update:%s, delete:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.find, self.find_email, self.find_confirmation, self.__opts.status,
                self.retrieve, self.create, self.update, self.__opts.delete, self.indent, self.verbose)
