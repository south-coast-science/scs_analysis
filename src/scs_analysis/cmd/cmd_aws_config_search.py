"""
Created on 30 Mar 2021

@author: Jade Page (jade.page@southcoastscience.com)
"""
import optparse


class CmdAWSConfigSearch(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-h HOSTNAME] [-i][-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--hostname", "-n", type="string", action="store", dest="hostname",
                                 help="the (partial) hostname to search for")

        # output

        self.__parser.add_option("--indent", "-i", action="store_true", dest="indent", default=False,
                                 help="pretty print the output ")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()

    def is_valid(self):
        # may be needed later...
        return True

    @property
    def hostname(self):
        return self.__opts.hostname

    @property
    def indent(self):
        return self.__opts.indent

    @property
    def verbose(self):
        return self.__opts.verbose

    def print_help(self, file):
        self.__parser.print_help(file)

    def __str__(self, *args, **kwargs):
        return "CmdAWSConfigSearch:{hostname:%s, indent:%s, verbose:%s}" % \
                    (self.hostname, self.indent, self.verbose)


