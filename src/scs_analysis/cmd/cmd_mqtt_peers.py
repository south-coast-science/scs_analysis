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
        self.__parser = optparse.OptionParser(usage="%prog [-a] { -p [-e] | -l [-n HOSTNAME] [-t TOPIC] | -m | "
                                                    "-c HOSTNAME TAG SHARED_SECRET TOPIC | "
                                                    "-u HOSTNAME { -s SHARED_SECRET | -t TOPIC } | "
                                                    "-r HOSTNAME } [-i INDENT] [-v]", version="%prog 1.0")

        # source...
        self.__parser.add_option("--aws", "-a", action="store_true", dest="aws", default=False,
                                 help="Use AWS S3 instead of local storage")

        # functions...
        self.__parser.add_option("--import", "-p", action="store_true", dest="import_peers", default=False,
                                 help="import MQTT peers from stdin")

        self.__parser.add_option("--list", "-l", action="store_true", dest="list", default=False,
                                 help="list the stored MQTT peers to stdout")

        self.__parser.add_option("--missing", "-m", action="store_true", dest="missing", default=False,
                                 help="list known devices missing from S3 MQTT peers")

        self.__parser.add_option("--create", "-c", type="string", nargs=4, action="store", dest="create",
                                 help="create an MQTT peer")

        self.__parser.add_option("--update", "-u", type="string", nargs=1, action="store", dest="update",
                                 help="update an MQTT peer")

        self.__parser.add_option("--remove", "-r", type="string", nargs=1, action="store", dest="remove",
                                 help="delete an MQTT peer")

        # filters...
        self.__parser.add_option("--hostname", "-n", type="string", nargs=1, action="store", dest="hostname",
                                 help="filter peers with the given hostname substring")

        self.__parser.add_option("--shared-secret", "-s", type="string", nargs=1, action="store", dest="shared_secret",
                                 help="specify shared secret")

        self.__parser.add_option("--topic", "-t", type="string", nargs=1, action="store", dest="topic",
                                 help="specify topic")

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

        if self.is_import():
            count += 1

        if self.missing:
            count += 1

        if self.list:
            count += 1

        if self.is_create():
            count += 1

        if self.is_update():
            count += 1

        if self.is_remove():
            count += 1

        if count != 1:
            return False

        if not self.is_import() and self.echo:
            return False

        if self.__opts.list is None and (self.__opts.hostname is not None or self.__opts.for_topic is not None):
            return False

        if self.missing and not self.aws:
            return False

        if self.echo and self.indent is not None:
            return False

        if self.is_update() and not self.shared_secret and not self.topic:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def is_import(self):
        return self.__opts.import_peers


    def is_create(self):
        return self.__opts.create is not None


    def is_update(self):
        return self.__opts.update is not None


    def is_remove(self):
        return self.__opts.remove is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def list(self):
        return self.__opts.list


    @property
    def missing(self):
        return self.__opts.missing


    @property
    def create_hostname(self):
        return None if self.__opts.create is None else self.__opts.create[0]


    @property
    def create_tag(self):
        return None if self.__opts.create is None else self.__opts.create[1]


    @property
    def create_shared_secret(self):
        return None if self.__opts.create is None else self.__opts.create[2]


    @property
    def create_topic(self):
        return None if self.__opts.create is None else self.__opts.create[3]


    @property
    def update_hostname(self):
        return self.__opts.update


    @property
    def remove_hostname(self):
        return self.__opts.remove


    @property
    def hostname(self):
        return self.__opts.hostname


    @property
    def shared_secret(self):
        return self.__opts.shared_secret


    @property
    def topic(self):
        return self.__opts.topic


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
        return "CmdMQTTPeers:{import:%s, list:%s, missing:%s, create:%s, update:%s, " \
               "remove:%s, hostname:%s, shared_secret:%s, topic:%s, aws:%s, echo:%s, indent:%s, " \
               "verbose:%s}" %  \
               (self.__opts.import_peers, self.list, self.missing, self.__opts.create, self.__opts.update,
                self.__opts.remove, self.hostname, self.shared_secret, self.topic, self.aws, self.echo, self.indent,
                self.verbose)
