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
        self.__parser = optparse.OptionParser(usage="%prog { -c EMAIL | -t EMAIL | -r EMAIL | -p EMAIL } [-v]",
                                              version="%prog 1.0")

        # operations...
        self.__parser.add_option("--resend-confirmation", "-c", type="string", action="store",
                                 dest="resend_confirmation", help="resend account confirmation email")

        self.__parser.add_option("--resend-temporary", "-t", type="string", action="store",
                                 dest="resend_temporary", help="resend temporary password email")

        self.__parser.add_option("--request-reset", "-r", type="string", action="store",
                                 dest="request_reset", help="request password reset code")

        self.__parser.add_option("--reset-password", "-p", type="string", action="store",
                                 dest="reset_password", help="perform password reset")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.resend_confirmation:
            count += 1

        if self.resend_temporary:
            count += 1

        if self.request_reset:
            count += 1

        if self.reset_password:
            count += 1

        if count != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def email(self):
        if self.resend_confirmation:
            return self.__opts.resend_confirmation

        if self.resend_temporary:
            return self.__opts.resend_temporary

        if self.request_reset:
            return self.__opts.request_reset

        if self.reset_password:
            return self.__opts.reset_password

        return None


    @property
    def resend_confirmation(self):
        return self.__opts.resend_confirmation is not None


    @property
    def resend_temporary(self):
        return self.__opts.resend_temporary is not None


    @property
    def request_reset(self):
        return self.__opts.request_reset is not None


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
        return "CmdCognitoPassword:{resend_confirmation:%s, resend_temporary:%s, request_reset:%s, " \
               "reset_password:%s, verbose:%s}" % \
               (self.__opts.resend_confirmation, self.__opts.resend_temporary, self.__opts.request_reset,
                self.__opts.reset_password, self.verbose)
