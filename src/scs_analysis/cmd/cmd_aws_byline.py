"""
Created on 25 Dec 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSByline(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] { -d DEVICE | -t TOPIC [-l] | -a } "
                                                    "[-x EXCLUDED] [-s] [-m] [-i INDENT] [-v]", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # search types...
        self.__parser.add_option("--device", "-d", type="string", action="store", dest="device",
                                 help="report bylines for DEVICE")

        self.__parser.add_option("--topic", "-t", type="string", action="store", dest="topic",
                                 help="report bylines for TOPIC")

        self.__parser.add_option("--all", "-a", action="store_true", dest="all", default=False,
                                 help="report all bylines")

        # filters...
        self.__parser.add_option("--excluded", "-x", type="string", action="store", dest="excluded",
                                 help="exclude topics ending with EXCLUDED")

        self.__parser.add_option("--strict", "-s", action="store_true", dest="strict", default=False,
                                 help="only report devices with valid tags")

        # output...
        self.__parser.add_option("--latest", "-l", action="store_true", dest="latest", default=False,
                                 help="only report the most recent byline")

        self.__parser.add_option("--include-messages", "-m", action="store_true", dest="include_messages",
                                 default=False, help="report the message with each byline")

        self.__parser.add_option("--indent", "-i", action="store", dest="indent", type=int,
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if bool(self.device):
            count += 1

        if bool(self.topic):
            count += 1

        if self.all:
            count += 1

        if count != 1:
            return False

        if self.latest and not bool(self.topic):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------
    # properties: identity...

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def device(self):
        return self.__opts.device


    @property
    def topic(self):
        return self.__opts.topic


    @property
    def latest(self):
        return self.__opts.latest


    @property
    def all(self):
        return self.__opts.all


    @property
    def excluded(self):
        return self.__opts.excluded


    @property
    def strict(self):
        return self.__opts.strict


    @property
    def include_messages(self):
        return self.__opts.include_messages


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
        return "CmdAWSByline:{credentials_name:%s, device:%s, topic:%s, latest:%s, all:%s, excluded:%s, strict:%s, " \
               "include_messages:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.device, self.topic, self.latest, self.all, self.excluded, self.strict,
                self.include_messages, self.indent, self.verbose)
