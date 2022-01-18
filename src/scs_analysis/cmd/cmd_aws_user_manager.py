"""
Created on 10 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSUserManager(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -F ORG_ID | -C ORG_ID EMAIL | -R ORG_ID EMAIL | "
                                                    "-U ORG_ID EMAIL  } "
                                                    "[-i INDENT] [-v]", version="%prog 1.0")

        # operations...
        self.__parser.add_option("--Find", "-F", type="int", action="store", dest="find",
                                 help="find the users for the given organisation")

        self.__parser.add_option("--Retrieve", "-R", type="string", nargs=2, action="store", dest="retrieve",
                                 help="retrieve the user for the given organisation and email")

        self.__parser.add_option("--Create", "-C", type="string", nargs=2, action="store", dest="create",
                                 help="create a user for the given organisation and email")

        self.__parser.add_option("--Update", "-U", type="string", nargs=2, action="store", dest="update",
                                 help="update the user for the given organisation and email")

        # fields...
        self.__parser.add_option("--given-name", "-g", type="string", action="store", dest="given_name",
                                 help="set the user's given name")

        self.__parser.add_option("--family-name", "-f", type="string", action="store", dest="family_name",
                                 help="set the user's family name")

        self.__parser.add_option("--email", "-e", type="string", action="store", dest="email",
                                 help="set the user's family email address")

        self.__parser.add_option("--administrator", "-a", type="int", action="store", dest="administrator",
                                 help="set the user's administrator status")

        self.__parser.add_option("--suspended", "-s", type="int", action="store", dest="email",
                                 help="set the user's suspended status")

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

        if self.update:
            count += 1

        if count != 1:
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
    def update(self):
        return self.__opts.update


    @property
    def name(self):
        return self.__opts.name


    @property
    def url(self):
        return self.__opts.url


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
        return "CmdAWSUserManager:{find:%s, retrieve:%s, update:%s, name:%s, url:%s, indent:%s, verbose:%s}" % \
               (self.find, self.retrieve, self.update, self.name, self.url, self.indent, self.verbose)
