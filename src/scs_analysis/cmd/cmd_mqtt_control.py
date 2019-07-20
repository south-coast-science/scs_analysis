"""
Created on 9 May 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdMQTTControl(object):
    """unix command line handler"""

    DEFAULT_TIMEOUT = 20                # seconds


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -p HOSTNAME | -d TAG SHARED_SECRET TOPIC } "
                                                    "{ -i | -r [CMD_TOKENS] } [-t TIMEOUT] [-v]", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--peer", "-p", type="string", nargs=1, action="store", dest="peer",
                                 help="use the stored MQTT peer")

        self.__parser.add_option("--device", "-d", type="string", nargs=3, action="store", dest="device",
                                 help="specify a tag, shared secret and topic for the peer")

        # optional...
        self.__parser.add_option("--receipt", "-r", action="store_true", dest="receipt", default=False,
                                 help="wait for receipt from target peer")

        self.__parser.add_option("--interactive", "-i", action="store_true", dest="interactive", default=False,
                                 help="interactive mode (always waits for receipt)")

        self.__parser.add_option("--timeout", "-t", type="int", nargs=1, action="store", dest="timeout",
                                 default=self.DEFAULT_TIMEOUT,
                                 help="receipt timeout in seconds (default %d)" % self.DEFAULT_TIMEOUT)

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.is_stored_peer() == self.is_device():
            return False

        if self.interactive == self.receipt:
            return False

        if self.interactive and self.cmd_tokens is not None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def is_stored_peer(self):
        return self.__opts.peer is not None


    def is_device(self):
        return self.__opts.device is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def peer_hostname(self):
        return self.__opts.peer


    @property
    def device_tag(self):
        return None if self.__opts.device is None else self.__opts.device[0]


    @property
    def device_shared_secret(self):
        return None if self.__opts.device is None else self.__opts.device[1]


    @property
    def device_topic(self):
        return None if self.__opts.device is None else self.__opts.device[2]


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


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdMQTTControl:{peer:%s, device:%s, cmd_tokens:%s, receipt:%s, interactive:%s, timeout:%s, " \
               "verbose:%s}" % \
               (self.__opts.peer, self.__opts.device, self.cmd_tokens, self.receipt, self.interactive, self.timeout,
                self.verbose)
