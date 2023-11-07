"""
Created on 22 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdCognitoEmail(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -e | -c | -s | -r } [-v] EMAIL",
                                              version=version())

        # operations...
        self.__parser.add_option("--send-email", "-e", action="store_true", dest="send_email",
                                 help="send access email")

        self.__parser.add_option("--confirm", "-c", action="store_true", dest="confirm",
                                 help="confirm account (using confirmation code)")

        self.__parser.add_option("--set-password", "-s", action="store_true", dest="set_password",
                                 help="set password (using temporary password)")

        self.__parser.add_option("--reset-password", "-r", action="store_true", dest="reset_password",
                                 help="reset password (using reset code)")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.send_email:
            count += 1

        if self.confirm:
            count += 1

        if self.set_password:
            count += 1

        if self.reset_password:
            count += 1

        if count != 1:
            return False

        if not self.__args or len(self.__args) != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def send_email(self):
        return self.__opts.send_email


    @property
    def confirm(self):
        return self.__opts.confirm


    @property
    def set_password(self):
        return self.__opts.set_password


    @property
    def reset_password(self):
        return self.__opts.reset_password


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def email(self):
        return self.__args[0] if self.__args else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCognitoEmail:{send_email:%s, confirm:%s, set_password:%s, reset:%s, verbose:%s}" % \
               (self.send_email, self.confirm, self.set_password, self.reset_password, self.verbose)
