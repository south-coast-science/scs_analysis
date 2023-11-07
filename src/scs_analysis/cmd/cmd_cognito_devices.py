"""
Created on 24 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdCognitoDevices(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog  [-c CREDENTIALS] "
                                                    "{ -F [{ -t TAG | -n INVOICE }] [-m] "
                                                    "| -U TAG INVOICE "
                                                    "| -D TAG } "
                                                    "[-i INDENT] [-v]",
                                              version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="list the devices visible to me")

        self.__parser.add_option("--Update", "-U", type="string", action="store", nargs=2, dest="update",
                                 help="update the device")

        self.__parser.add_option("--Delete", "-D", type="string", action="store", dest="delete",
                                 help="delete the device (superuser only)")

        # filters...
        self.__parser.add_option("--tag", "-t", type="string", action="store", dest="tag",
                                 help="filter by device tag")

        self.__parser.add_option("--invoice", "-n", type="string", action="store", dest="invoice_number",
                                 help="filter by invoice")

        # output...
        self.__parser.add_option("--memberships", "-m", action="store_true", dest="memberships", default=False,
                                 help="show device's organisation memberships")

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

        if self.update:
            count += 1

        if self.delete is not None:
            count += 1

        if count != 1:
            return False

        if self.memberships and not self.find:
            return False

        if self.tag and self.invoice_number:
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
    def update(self):
        return bool(self.__opts.update)


    @property
    def update_tag(self):
        return self.__opts.update[0] if self.update else None


    @property
    def update_invoice(self):
        return self.__opts.update[1] if self.update else None


    @property
    def delete(self):
        return self.__opts.delete


    @property
    def tag(self):
        return self.__opts.tag


    @property
    def invoice_number(self):
        return self.__opts.invoice_number


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
        return "CmdCognitoDevices:{credentials_name:%s, find:%s, update:%s, delete:%s, " \
               "tag:%s, invoice:%s, memberships:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.find, self.update, self.delete,
                self.tag, self.invoice_number, self.memberships, self.indent, self.verbose)
