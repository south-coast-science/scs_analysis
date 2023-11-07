"""
Created on 28 Jun 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdDeviceMonitor(object):
    """unix command line handler"""

    # --------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] "
                                                    "{ -F [{ -e EMAIL_ADDR | -t DEVICE_TAG } [-x]] | "
                                                    "-A EMAIL_ADDR DEVICE_TAG [-j] | -S DEVICE_TAG { 0 | 1 } | "
                                                    "-D EMAIL_ADDR -t DEVICE_TAG } "
                                                    "[-i INDENT] [-v]", version=version())

        # [{ -t DEVICE_TAG | -f }]

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--find", "-F", action="store_true", dest="find", default=False,
                                 help="find monitoring (for email address or device)")

        self.__parser.add_option("--add", "-A", type="string", nargs=2, action="store", dest="add",
                                 help="add email address to device")

        self.__parser.add_option("--suspend", "-S", type="string", nargs=2, action="store", dest="suspend",
                                 help="suspend monitoring of the device")

        self.__parser.add_option("--delete", "-D", type="string", action="store", dest="delete",
                                 help="delete email address (from device or throughout)")

        # self.__parser.add_option("--force", "-f", type="string", action="store", dest="force",
        #                          help="force deletion from multiple devices")

        # fields...
        self.__parser.add_option("--json-message", "-j", action="store_true", dest="json_message", default=False,
                                 help="message body is JSON")

        # filters...
        self.__parser.add_option("--email", "-e", type="string", action="store", dest="email",
                                 help="email address")

        self.__parser.add_option("--device-tag", "-t", type="string", action="store", dest="device_tag",
                                 help="device tag")

        self.__parser.add_option("--exactly", "-x", action="store_true", dest="exact_match", default=False,
                                 help="exact match for tag")

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

        if self.add:
            count += 1

        if self.suspend:
            count += 1

        if self.delete:
            count += 1

        if count != 1:
            return False

        if not self.add and self.json_message:
            return False

        if self.suspend and self.__opts.suspend[1] not in [None, '0', '1']:
            return False

        if self.__args:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------
    # properties: identity...

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    # ----------------------------------------------------------------------------------------------------------------
    # properties: operations...

    @property
    def find(self):
        return self.__opts.find


    @property
    def add(self):
        return bool(self.__opts.add)


    @property
    def suspend(self):
        return bool(self.__opts.suspend)


    @property
    def is_suspended(self):
        return bool(int(self.__opts.suspend[1])) if self.suspend else None


    @property
    def delete(self):
        return bool(self.__opts.delete)


    # ----------------------------------------------------------------------------------------------------------------
    # properties: fields...

    @property
    def json_message(self):
        return self.__opts.json_message


    # ----------------------------------------------------------------------------------------------------------------
    # properties: filters...

    @property
    def email(self):
        if self.add:
            return self.__opts.add[0]

        if self.delete:
            return self.__opts.delete

        return self.__opts.email


    @property
    def device_tag(self):
        if self.add:
            return self.__opts.add[1]

        if self.suspend:
            return self.__opts.suspend[0]

        return self.__opts.device_tag


    @property
    def exact_match(self):
        return self.__opts.exact_match


    # ----------------------------------------------------------------------------------------------------------------
    # properties: output...

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
        return "CmdDeviceMonitor:{credentials_name:%s, find:%s, add:%s, suspend:%s, delete:%s, " \
               "email:%s, device_tag:%s, json_message:%s, exact_match:%s, " \
               "indent:%s, verbose:%s}" % \
               (self.credentials_name, self.__opts.find, self.__opts.add, self.__opts.suspend, self.__opts.delete,
                self.__opts.email, self.__opts.device_tag, self.json_message, self.exact_match,
                self.indent, self.verbose)
