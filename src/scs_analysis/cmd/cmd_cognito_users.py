"""
Created on 24 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version
from scs_core.aws.security.cognito_user import CognitoUserIdentity


# --------------------------------------------------------------------------------------------------------------------

class CmdCognitoUsers(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        confirmations = ' | '.join(CognitoUserIdentity.status_codes())

        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] "
                                                    "{ -F [{ -e EMAIL_ADDR | -l ORG_LABEL | -o CONFIRMATION | "
                                                    "-s { 0 | 1 } } }] [-m] "
                                                    "| -C -g GIVEN_NAME -f FAMILY_NAME -e EMAIL_ADDR "
                                                    "| -U EMAIL_ADDR [-g GIVEN_NAME] [-f FAMILY_NAME] [-e EMAIL_ADDR] "
                                                    "[-s { 0 | 1 }] "
                                                    "| -D EMAIL_ADDR } "
                                                    "[-i INDENT] [-v]",
                                              version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="list the users visible to me")

        self.__parser.add_option("--Create", "-C", action="store_true", dest="create", default=False,
                                 help="create a user")

        self.__parser.add_option("--Update", "-U", type="string", action="store", dest="update",
                                 help="update the user")

        self.__parser.add_option("--Delete", "-D", type="string", action="store", dest="delete",
                                 help="delete the user (superuser only)")

        # filters...
        self.__parser.add_option("--given-name", "-g", type="string", action="store", dest="given_name",
                                 help="given name")

        self.__parser.add_option("--family-name", "-f", type="string", action="store", dest="family_name",
                                 help="family name")

        self.__parser.add_option("--email", "-e", type="string", action="store", dest="email",
                                 help="email address")

        self.__parser.add_option("--org-label", "-l", type="string", action="store", dest="org_label",
                                 help="the organisation label")

        self.__parser.add_option("--confirmation-status", "-o", type="string", action="store",
                                 dest="confirmation_status",
                                 help="filter list by confirmation status { %s }" % confirmations)

        self.__parser.add_option("--enabled-status", "-s", type="int", action="store", dest="enabled",
                                 help="filter list by enabled status { 0 | 1 }")

        # output...
        self.__parser.add_option("--memberships", "-m", action="store_true", dest="memberships", default=False,
                                 help="show user's organisation memberships")

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

        count = 0

        if self.find:
            if self.org_label is not None:
                count += 1

            if self.email is not None:
                count += 1

            if self.confirmation_status is not None:
                count += 1

            if self.enabled is not None:
                count += 1

            if count > 1:
                return False

        if self.memberships and not self.find:
            return False

        if self.confirmation_status is not None and self.confirmation_status not in CognitoUserIdentity.status_codes():
            return False

        if self.enabled is not None and self.enabled not in (0, 1):
            return None

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
    def given_name(self):
        return self.__opts.given_name


    @property
    def family_name(self):
        return self.__opts.family_name


    @property
    def email(self):
        return self.__opts.email


    @property
    def org_label(self):
        return self.__opts.org_label


    @property
    def confirmation_status(self):
        return self.__opts.confirmation_status


    @property
    def enabled(self):
        return self.__opts.enabled


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
        return "CmdCognitoUsers:{credentials_name:%s, find:%s, create:%s, update:%s, delete:%s, " \
               "given_name:%s, family_name:%s, email:%s, org_label:%s, confirmation_status:%s, " \
               "enabled:%s, memberships:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.find, self.create, self.update, self.delete,
                self.given_name, self.family_name, self.email, self.org_label, self.confirmation_status,
                self.enabled, self.memberships, self.indent, self.verbose)
