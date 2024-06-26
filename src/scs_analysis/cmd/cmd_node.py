"""
Created on 25 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version

from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

class CmdNode(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-m FROM TO] [-x] [-a] [-s] [-f FILE] [-i INDENT] [-v] "
                                                    "[NODE_1 .. NODE_N]", version=version())

        # mode...
        self.__parser.add_option("--move", "-m", type="string", nargs=2, action="store", dest="move",
                                 help="move the node at FROM to TO")

        self.__parser.add_option("--exclude", "-x", action="store_true", dest="exclude", default=False,
                                 help="include all nodes except the named one(s)")

        self.__parser.add_option("--array", "-a", action="store_true", dest="array", default=False,
                                 help="output the sequence of input JSON documents as array")

        self.__parser.add_option("--sequence", "-s", action="store_true", dest="sequence", default=False,
                                 help="output the contents of the input array node(s) as a sequence")

        self.__parser.add_option("--file", "-f", type="string", action="store", dest="filename",
                                 help="read from FILE instead of stdin")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def is_valid(cls):
        return True


    def includes(self, path):
        for sub_path in self.sub_paths:
            if PathDict.sub_path_includes_path(sub_path, path):
                return not self.exclude

        return self.exclude


    def has_sub_paths(self):
        return bool(self.__args)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exclude(self):
        return self.__opts.exclude


    @property
    def move(self):
        return bool(self.__opts.move)


    @property
    def move_from(self):
        return self.__opts.move[0] if self.__opts.move else None


    @property
    def move_to(self):
        return self.__opts.move[1] if self.__opts.move else None


    @property
    def array(self):
        return self.__opts.array


    @property
    def sequence(self):
        return self.__opts.sequence


    @property
    def filename(self):
        return self.__opts.filename


    @property
    def indent(self):
        return self.__opts.indent


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def sub_paths(self):
        return self.__args if self.__args else [None]           # if empty return only the root node


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return ("CmdNode:{move:%s, exclude:%s, array:%s, sequence:%s, filename:%s, "
                "indent:%s, verbose:%s, sub_paths:%s}") %  \
               (self.__opts.move, self.exclude, self.array, self.sequence, self.filename,
                self.indent, self.verbose, self.__args)
