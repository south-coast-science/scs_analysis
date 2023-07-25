"""
Created on 22 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_airnow import version


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVJoin(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-t TYPE] [-i] [-v] -l PREFIX PK FILENAME "
                                                    "-r PREFIX PK FILENAME", version=version())

        # input...
        self.__parser.add_option("--left", "-l", type="string", nargs=3, action="store", dest="left",
                                 help="output path prefix, primary key and filename for left-hand set")

        self.__parser.add_option("--right", "-r", type="string", nargs=3, action="store", dest="right",
                                 help="output path prefix, primary key and filename for right-hand set")

        # mode...
        self.__parser.add_option("--type", "-t", type="string", action="store", dest="type", default='INNER',
                                 help="{ 'INNER' | 'LEFT' | 'RIGHT' | 'FULL' } (default 'INNER')")

        self.__parser.add_option("--iso8601", "-i", action="store_true", dest="iso8601", default=False,
                                 help="interpret the primary key as an ISO 8601 datetime")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.left is None or self.__opts.right is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def type(self):
        return self.__opts.type


    @property
    def left_prefix(self):
        return None if self.__opts.left is None else self.__opts.left[0]


    @property
    def left_pk(self):
        return None if self.__opts.left is None else self.__opts.left[1]


    @property
    def left_filename(self):
        return None if self.__opts.left is None else self.__opts.left[2]


    @property
    def right_prefix(self):
        return None if self.__opts.right is None else self.__opts.right[0]


    @property
    def right_pk(self):
        return None if self.__opts.right is None else self.__opts.right[1]


    @property
    def right_filename(self):
        return None if self.__opts.right is None else self.__opts.right[2]


    @property
    def iso8601(self):
        return self.__opts.iso8601


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCSVJoin:{type:%s, left:%s, right:%s, iso8601:%s, verbose:%s}" % \
               (self.type, self.__opts.left, self.__opts.right, self.iso8601, self.verbose)
