"""
Created on 9 May 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdOSIOMQTTControl(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -d TAG HOST_ID TOPIC { -i | [-r] CMD } [-t TIMEOUT] [-v]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--device", "-d", type="string", nargs=3, action="store", dest="tag_host_topic",
                                 help="tag and host ID of target device")

        # optional...
        self.__parser.add_option("--receipt", "-r", action="store_true", dest="receipt", default=False,
                                 help="wait for receipt from target device")

        self.__parser.add_option("--interactive", "-i", action="store_true", dest="interactive", default=False,
                                 help="interactive mode (always waits for receipt)")

        self.__parser.add_option("--timeout", "-t", type="int", nargs=1, action="store", dest="timeout", default=10,
                                 help="receipt timeout (default 10 seconds)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.interactive == self.receipt:
            return False

        if self.interactive and self.cmd_tokens is not None:
            return False

        return bool(self.__opts.tag_host_topic)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def device_tag(self):
        return self.__opts.tag_host_topic[0] if self.__opts.tag_host_topic else None


    @property
    def device_host_id(self):
        return self.__opts.tag_host_topic[1] if self.__opts.tag_host_topic else None


    @property
    def topic(self):
        return self.__opts.tag_host_topic[2] if self.__opts.tag_host_topic else None


    @property
    def cmd_tokens(self):
        return self.__args[0].split() if len(self.__args) > 0 else None


    @property
    def receipt(self):
        return self.__opts.receipt


    @property
    def interactive(self):
        return self.__opts.interactive


    @property
    def timeout(self):
        return self.__opts.timeout


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdOSIOMQTTControl:{tag_host:%s, topic:%s, cmd_tokens:%s, receipt:%s, interactive:%s, timeout:%s, " \
               "verbose:%s, args:%s}" % \
               (self.__opts.tag_host_topic, self.topic, self.cmd_tokens, self.receipt, self.interactive, self.timeout,
                self.verbose, self.args)
