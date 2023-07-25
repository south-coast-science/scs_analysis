"""
Created on 2 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVWriter(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ -a | -x | -s }] [-q] [-e] [-v] [FILENAME]",
                                              version=version())

        # mode...
        self.__parser.add_option("--append", "-a", action="store_true", dest="append", default=False,
                                 help="append rows to existing file")

        self.__parser.add_option("--exclude-header", "-x", action="store_true", dest="exclude_header", default=False,
                                 help="do not write the header row to stdout")

        self.__parser.add_option("--header-scan", "-s", action="store_true", dest="header_scan", default=False,
                                 help="scan all documents before building the header row")

        # output...
        self.__parser.add_option("--quote-all", "-q", action="store_true", dest="quote_all", default=False,
                                 help="wrap all CSV cell values in quotes")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.append:
            count += 1

        if self.exclude_header:
            count += 1

        if self.header_scan:
            count += 1

        if count > 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def append(self):
        return self.__opts.append


    @property
    def exclude_header(self):
        return self.__opts.exclude_header


    @property
    def header_scan(self):
        return self.__opts.header_scan


    @property
    def quote_all(self):
        return self.__opts.quote_all


    @property
    def echo(self):
        return self.__opts.echo


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def filename(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCSVWriter:{append:%s, exclude_header:%s, header_scan:%s, quote_all:%s, echo:%s, " \
               "verbose:%s, filename:%s}" % \
                    (self.append, self.exclude_header, self.header_scan, self.quote_all, self.echo,
                     self.verbose, self.filename)
