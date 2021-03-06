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
        self.__parser = optparse.OptionParser(usage="%prog { -p [-e] | -l [-n HOSTNAME] [-t TOPIC] | -m | -s "
                                                    "HOSTNAME TAG SHARED_SECRET TOPIC | -d HOSTNAME } "
                                                    "[-a] [-i INDENT] [-v]", version="%prog 1.0")

        # functions...
        self.__parser.add_option("--import", "-p", action="store_true", dest="import_peers", default=False,
                                 help="import MQTT peers from stdin")

        self.__parser.add_option("--list", "-l", action="store_true", dest="list", default=False,
                                 help="list the stored MQTT peers to stdout")

        self.__parser.add_option("--missing", "-m", action="store_true", dest="missing", default=False,
                                 help="list known devices missing from S3 MQTT peers")

        self.__parser.add_option("--set", "-s", type="string", nargs=4, action="store", dest="peer",
                                 help="insert or update an MQTT peer")

        self.__parser.add_option("--delete", "-d", type="string", nargs=1, action="store", dest="delete",
                                 help="delete an MQTT peer")

        # filters...
        self.__parser.add_option("--hostname", "-n", type="string", nargs=1, action="store", dest="for_hostname",
                                 help="filter peers with the given hostname substring")

        self.__parser.add_option("--topic", "-t", type="string", nargs=1, action="store", dest="for_topic",
                                 help="filter peers with the given topic substring")

        # source...
        self.__parser.add_option("--aws", "-a", action="store_true", dest="aws", default=False,
                                 help="Use AWS S3 instead of local storage")

        # output...
        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout (import only)")

        self.__parser.add_option("--indent", "-i", type="int", nargs=1, action="store", dest="indent",
                                 help="pretty-print the output with INDENT (not with echo)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.__opts.import_peers:
            count += 1

        if self.missing:
            count += 1

        if self.list:
            count += 1

        if self.__opts.peer is not None:
            count += 1

        if self.__opts.delete is not None:
            count += 1

        if count != 1:
            return False

        if not self.__opts.import_peers and self.echo:
            return False

        if self.__opts.list is None and (self.__opts.for_hostname is not None or self.__opts.for_topic is not None):
            return False

        if self.missing and not self.aws:
            return False

        if self.echo and self.indent is not None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def is_import_peers(self):
        return self.__opts.import_peers


    def is_set_peer(self):
        return self.__opts.peer is not None


    def is_delete_peer(self):
        return self.__opts.delete is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def list(self):
        return self.__opts.list


    @property
    def missing(self):
        return self.__opts.missing


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
    def for_hostname(self):
        return self.__opts.for_hostname


    @property
    def for_topic(self):
        return self.__opts.for_topic


    @property
    def aws(self):
        return self.__opts.aws


    @property
    def echo(self):
        return self.__opts.echo


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
        return "CmdMQTTPeers:{import:%s, list:%s, for_hostname:%s, for_topic:%s, missing:%s, set:%s, " \
               "delete:%s, aws:%s, echo:%s, indent:%s, verbose:%s}" %  \
               (self.__opts.import_peers, self.list, self.for_hostname, self.for_topic, self.missing, self.__opts.peer,
                self.__opts.delete, self.aws, self.echo, self.indent, self.verbose)

