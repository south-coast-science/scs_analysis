"""
Created on 22 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdCognitoPassword(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -e | -s | -r } EMAIL [-v]",
                                              version="%prog 1.0")

        # functions...
        self.__parser.add_option("--send-email", "-e", type="string", action="store", dest="send_email",
                                 help="send password email")

        self.__parser.add_option("--set-password", "-s", type="string", action="store", dest="set_password",
                                 help="set password (using temporary password)")

        self.__parser.add_option("--reset-password", "-r", type="string", action="store", dest="reset_password",
                                 help="reset password (using code)")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.send_email:
            count += 1

        if self.set_password:
            count += 1

        if self.reset_password:
            count += 1

        if count != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def email(self):
        if self.send_email:
            return self.__opts.send_email

        if self.set_password:
            return self.__opts.set_password

        if self.reset_password:
            return self.__opts.reset_password

        return None


    @property
    def send_email(self):
        return self.__opts.send_email is not None


    @property
    def set_password(self):
        return self.__opts.set_password is not None


    @property
    def reset_password(self):
        return self.__opts.reset_password is not None


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCognitoPassword:{send_email:%s, set_password:%s, reset:%s, verbose:%s}" % \
               (self.__opts.send_email, self.__opts.set_password, self.__opts.reset_password, self.verbose)
