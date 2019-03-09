"""
Created on 9 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdMQTTControlAuth(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -l | [-s HOSTNAME TAG SHARED_SECRET TOPIC] "
                                                    "[-d HOSTNAME] } [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--list", "-l", action="store_true", dest="list", default=False,
                                 help="list the stored MQTT control auth documents to stdout")

        self.__parser.add_option("--set", "-s", type="string", nargs=4, action="store", dest="auth",
                                 help="insert or update an MQTT control auth document")

        self.__parser.add_option("--delete", "-d", type="string", nargs=1, action="store", dest="delete",
                                 help="delete an MQTT control auth document")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.list and (self.is_set_auth() or self.is_delete_auth()):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def is_set_auth(self):
        return self.__opts.auth is not None


    def is_delete_auth(self):
        return self.__opts.delete is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def list(self):
        return self.__opts.list


    @property
    def auth_hostname(self):
        return None if self.__opts.auth is None else self.__opts.auth[0]


    @property
    def auth_tag(self):
        return None if self.__opts.auth is None else self.__opts.auth[1]


    @property
    def auth_shared_secret(self):
        return None if self.__opts.auth is None else self.__opts.auth[2]


    @property
    def auth_topic(self):
        return None if self.__opts.auth is None else self.__opts.auth[3]


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
        return "CmdMQTTControlAuth:{list:%s, auth:%s, delete:%s, verbose:%s}" %  \
               (self.list, self.__opts.auth, self.__opts.delete, self.verbose)
