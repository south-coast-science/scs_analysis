"""
Created on 9 May 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdOSIODeviceControl(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -d TAG HOST_ID -t TOPIC -p UDS_PUB [-s UDS_SUB] [-v] [CMD]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--device", "-d", type="string", nargs=2, action="store", dest="tag_host",
                                 help="tag and host ID of target device")

        self.__parser.add_option("--topic", "-t", type="string", nargs=1, action="store", dest="topic",
                                 help="full topic path")

        self.__parser.add_option("--pub-addr", "-p", type="string", nargs=1, action="store", dest="uds_pub_addr",
                                 help="publish commands to UDS_PUB_ADDR")

        # optional...
        self.__parser.add_option("--sub-addr", "-s", type="string", nargs=1, action="store", dest="uds_sub_addr",
                                 help="subscribe to receipts from UDS_SUB_ADDR")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        return self.__opts.tag_host and self.__opts.topic and self.__opts.uds_pub_addr


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def device_tag(self):
        return self.__opts.tag_host[0] if self.__opts.tag_host else None


    @property
    def device_host_id(self):
        return self.__opts.tag_host[1] if self.__opts.tag_host else None


    @property
    def topic(self):
        return self.__opts.topic


    @property
    def uds_pub_addr(self):
        return self.__opts.uds_pub_addr


    @property
    def uds_sub_addr(self):
        return self.__opts.uds_sub_addr


    @property
    def cmd_tokens(self):
        return self.__args[0].split() if len(self.__args) > 0 else None


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
        return "CmdOSIODeviceControl:{tag_host:%s, topic:%s, uds_pub_addr:%s, uds_sub_addr:%s, cmd_tokens:%s, " \
               "verbose:%s, args:%s}" % \
               (self.__opts.tag_host, self.topic, self.uds_pub_addr, self.uds_sub_addr, self.cmd_tokens,
                self.verbose, self.args)
