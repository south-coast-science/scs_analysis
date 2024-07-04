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
        self.__parser = optparse.OptionParser(usage="%prog [-r FROM TO] [-m A B JOIN] [-x] [-a] [-s] [-f FILE] "
                                                    "[-i INDENT] [-v] [NODE_1 .. NODE_N]", version=version())

        # mode...
        self.__parser.add_option("--rename", "-r", type="string", nargs=2, action="store", dest="rename",
                                 help="move the node at FROM to TO")

        self.__parser.add_option("--merge", "-m", type="string", nargs=3, action="store", dest="merge",
                                 help="merge A and B")

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
    def rename(self):
        return bool(self.__opts.rename)


    @property
    def rename_from(self):
        return self.__opts.move[0] if self.__opts.move else None


    @property
    def rename_to(self):
        return self.__opts.move[1] if self.__opts.move else None


    @property
    def merge(self):
        return bool(self.__opts.merge)


    @property
    def merge_a(self):
        return self.__opts.merge[0] if self.__opts.merge else None


    @property
    def merge_b(self):
        return self.__opts.merge[1] if self.__opts.merge else None


    @property
    def merge_join(self):
        return self.__opts.merge[2] if self.__opts.merge else None


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
        if not self.__args:
            return [None]                   # if empty return only the root node

        sub_paths = self.__args

        if self.merge and self.merge_a not in sub_paths:
            sub_paths.insert(0, self.merge_a)

        if self.rename and self.rename_to not in sub_paths:
            sub_paths.insert(0, self.rename_to)

        return sub_paths


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdNode:{rename:%s, merge:%s, exclude:%s, array:%s, sequence:%s, filename:%s, " \
                "indent:%s, verbose:%s, sub_paths:%s}" %  \
               (self.__opts.rename, self.__opts.merge, self.exclude, self.array, self.sequence, self.filename,
                self.indent, self.verbose, self.__args)
