"""
Created on 9 Apr 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSTopicOrigin(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] [-i INDENT] [-v] TOPIC", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # filters...
        self.__parser.add_option("--indent", "-i", action="store", dest="indent", type=int,
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if not self.__args or len(self.__args) != 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------
    # properties: identity...

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def topic(self):
        return None if self.__args is None else self.__args[0]


    # ----------------------------------------------------------------------------------------------------------------
    # properties: output...

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
        return "CmdAWSTopicOrigin:{credentials_name:%s, indent:%s, verbose:%s, topic:%s}" % \
               (self.credentials_name, self.indent, self.verbose, self.topic)
