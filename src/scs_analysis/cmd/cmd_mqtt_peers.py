"""
Created on 9 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdMQTTPeers(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -l [-f HOSTNAME] | [-s HOSTNAME TAG SHARED_SECRET TOPIC] "
                                                    "[-d HOSTNAME] } [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--list", "-l", action="store_true", dest="list", default=False,
                                 help="list the stored MQTT peers to stdout")

        self.__parser.add_option("--find", "-f", type="string", nargs=1, action="store", dest="find",
                                 help="find the MQTT peer with the given hostname substring")

        self.__parser.add_option("--set", "-s", type="string", nargs=4, action="store", dest="peer",
                                 help="insert or update an MQTT peer")

        self.__parser.add_option("--delete", "-d", type="string", nargs=1, action="store", dest="delete",
                                 help="delete an MQTT peer")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.list and (self.is_set_peer() or self.is_delete_peer()):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def is_set_peer(self):
        return self.__opts.peer is not None


    def is_find_peer(self):
        return self.__opts.find is not None


    def is_delete_peer(self):
        return self.__opts.delete is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def list(self):
        return self.__opts.list


    @property
    def find_hostname(self):
        return self.__opts.find


    @property
    def set_hostname(self):
        return None if self.__opts.peer is None else self.__opts.peer[0]


    @property
    def set_tag(self):
        return None if self.__opts.peer is None else self.__opts.peer[1]


    @property
    def set_shared_secret(self):
        return None if self.__opts.peer is None else self.__opts.peer[2]


    @property
    def set_topic(self):
        return None if self.__opts.peer is None else self.__opts.peer[3]


    @property
    def delete_hostname(self):
        return self.__opts.delete


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdMQTTPeers:{list:%s, find:%s, set:%s, delete:%s, verbose:%s}" %  \
               (self.list, self.__opts.find, self.__opts.peer, self.__opts.delete, self.verbose)
