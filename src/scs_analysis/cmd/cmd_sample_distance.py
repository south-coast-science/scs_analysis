"""
Created on 11 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdSampleDistance(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -p LAT LNG [-i ISO] [-q QUALITY] [-v] GPS_PATH",
                                              version=version())

        # compulsory...
        self.__parser.add_option("--position", "-p", type="float", nargs=2, action="store", dest="position",
                                 help="position (in degrees)")

        # optional...
        self.__parser.add_option("--iso-path", "-i", type="string", action="store", default="rec", dest="iso",
                                 help="path for ISO 8601 datetime output (default 'rec')")

        self.__parser.add_option("--quality", "-q", type="int", action="store", dest="quality",
                                 help="minimum acceptable GPS quality")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.position is None or self.path is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def position(self):
        return self.__opts.position


    @property
    def lat(self):
        return None if self.__opts.position is None else self.__opts.position[0]


    @property
    def lng(self):
        return None if self.__opts.position is None else self.__opts.position[1]


    @property
    def iso(self):
        return self.__opts.iso


    @property
    def quality(self):
        return self.__opts.quality


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampleDistance:{position:%s, iso:%s, quality:%s, verbose:%s, path:%s}" % \
               (self.position, self.iso, self.quality, self.verbose, self.path)
