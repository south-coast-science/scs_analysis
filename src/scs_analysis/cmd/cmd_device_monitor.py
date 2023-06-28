"""
Created on 28 Jun 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdDeviceMonitor(object):
    """unix command line handler"""

    # --------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] { -F [{ -e EMAIL_ADDR | -t DEVICE_TAG }] | "
                                                    "-A EMAIL_ADDR DEVICE_TAG | -D EMAIL_ADDR [-t DEVICE_TAG] } "
                                                    "[-i INDENT] [-v]", version="%prog 1.0")

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--find", "-F", action="store_true", dest="find", default=False,
                                 help="find monitoring (for email address or device)")

        self.__parser.add_option("--add", "-A", type="string", nargs=2, action="store", dest="add",
                                 help="add email address to device")

        self.__parser.add_option("--delete", "-D", type="string", action="store", dest="delete",
                                 help="delete email address (from device or throughout)")

        # filters...
        self.__parser.add_option("--email", "-e", type="string", action="store", dest="email",
                                 help="email address")

        self.__parser.add_option("--device-tag", "-t", type="string", action="store", dest="device_tag",
                                 help="device tag")

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

        if self.add:
            count += 1

        if self.delete:
            count += 1

        if count != 1:
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
    def delete(self):
        return bool(self.__opts.delete)


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

        return self.__opts.device_tag


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
        return "CmdDeviceMonitor:{credentials_name:%s, find:%s, add:%s, delete:%s, " \
               "email:%s, device_tag:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.__opts.find, self.__opts.add, self.__opts.delete,
                self.__opts.email, self.__opts.device_tag, self.indent, self.verbose)