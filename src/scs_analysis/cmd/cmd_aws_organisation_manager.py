"""
Created on 10 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSOrganisationManager(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog  { -F | -R ORG_ID | -U ORG_ID [-n NAME] [-u URL] } "
                                                    "[-i INDENT] [-v]", version="%prog 1.0")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="find the organisations I belong to")

        self.__parser.add_option("--Retrieve", "-R", type="int", action="store", dest="retrieve",
                                 help="retrieve the organisation with the given ID")

        self.__parser.add_option("--Update", "-U", type="int", action="store", dest="update",
                                 help="update the organisation with the given ID")

        # fields...
        self.__parser.add_option("--name", "-n", type="string", action="store", dest="name",
                                 help="set the organisation name")

        self.__parser.add_option("--url", "-u", type="string", action="store", dest="url",
                                 help="set the organisation URL")

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
        return "CmdAWSOrganisationManager:{find:%s, retrieve:%s, update:%s, name:%s, url:%s, indent:%s, verbose:%s}" % \
               (self.find, self.retrieve, self.update, self.name, self.url, self.indent, self.verbose)
