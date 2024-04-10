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
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] [-i INDENT] [-v] "
                                                    "{ -a | -d DEVICE | -t TOPIC_1 [...TOPIC_N] }",
                                              version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # topic sources...
        self.__parser.add_option("--all", "-a", action="store_true", dest="all", default=False,
                                 help="all topics")

        self.__parser.add_option("--device", "-d", type="string", action="store", dest="device",
                                 help="topics for DEVICE")

        self.__parser.add_option("--topics", "-t", action="store_true", dest="topics", default=False,
                                 help="named topics")


        # output...
        self.__parser.add_option("--indent", "-i", action="store", dest="indent", type=int,
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.all:
            count += 1

        if self.device is not None:
            count += 1

        if self.topics:
            count += 1

        if count != 1:
            return False

        if self.topics and not self.requested_topics:
            return False

        if not self.topics and self.requested_topics:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------
    # properties: identity...

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    # ----------------------------------------------------------------------------------------------------------------
    # properties: topic sources...

    @property
    def all(self):
        return self.__opts.all


    @property
    def device(self):
        return self.__opts.device


    @property
    def topics(self):
        return self.__opts.topics


    @property
    def requested_topics(self):
        return self.__args


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
        return ("CmdAWSTopicOrigin:{credentials_name:%s, all:%s, device:%s, topics:%s, indent:%s, verbose:%s, "
                "requested_topics:%s}") % \
               (self.credentials_name, self.all, self.device, self.topics, self.indent, self.verbose,
                self.requested_topics)
