"""
Created on 24 Nov 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdCognitoManager(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog  { -l [-e EMAIL_ADDR] | -r | -c | -u } [-i INDENT] [-v]",
                                              version="%prog 1.0")

        # operations...
        self.__parser.add_option("--list", "-l", action="store_true", dest="find", default=False,
                                 help="list the identities visible to me")

        self.__parser.add_option("--retrieve", "-r", action="store_true", dest="retrieve", default=False,
                                 help="retrieve my identity")

        self.__parser.add_option("--create", "-c", action="store_true", dest="create", default=False,
                                 help="create my identity")

        self.__parser.add_option("--update", "-u", action="store_true", dest="update", default=False,
                                 help="update my identity")

        # email...
        self.__parser.add_option("--email", "-e", type="string", action="store", dest="email",
                                 help="email address (partial match)")

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

        if self.retrieve:
            count += 1

        if self.create:
            count += 1

        if self.update:
            count += 1

        if count != 1:
            return False

        if self.email is not None and not self.find:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

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
        return self.__opts.delete_id is not None


    @property
    def email(self):
        return self.__opts.email


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
        return "CmdCognitoManager:{find:%s, retrieve:%s, create:%s, update:%s, email:%s, indent:%s, verbose:%s}" % \
               (self.find, self.retrieve, self.create, self.update, self.email, self.indent, self.verbose)
