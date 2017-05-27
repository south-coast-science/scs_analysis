"""
Created on 23 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdOSIOMQTTClient(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [SUB_TOPIC_1 .. SUB_TOPIC_N] [-p UDS_PUB] [-s UDS_SUB] [-e] "
                                                    "[-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--pub-addr", "-p", type="string", nargs=1, action="store", dest="uds_pub_addr",
                                 help="read publications from UDS instead of stdin")

        self.__parser.add_option("--sub-addr", "-s", type="string", nargs=1, action="store", dest="uds_sub_addr",
                                 help="write subscriptions to UDS instead of stdout")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo input to stdout (if writing subscriptions to UDS)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.echo and self.__opts.uds_sub_addr is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def topics(self):
        return self.__args


    @property
    def uds_pub_addr(self):
        return self.__opts.uds_pub_addr


    @property
    def uds_sub_addr(self):
        return self.__opts.uds_sub_addr


    @property
    def echo(self):
        return self.__opts.echo


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
        return "CmdOSIOMQTTClient:{topics:%s, uds_pub_addr:%s, uds_sub_addr:%s, echo:%s, verbose:%s, args:%s}" % \
               (self.topics, self.uds_pub_addr, self.uds_sub_addr, self.echo, self.verbose, self.args)
