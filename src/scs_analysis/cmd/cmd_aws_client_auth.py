"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

example document:
{"org-id": "south-coast-science-test-user", "api-key": "9fdfb841-3433-45b8-b223-3f5a283ceb8e"}
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSClientAuth(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ [-e ENDPOINT] [-c CLIENT_ID] [-I CERT_ID] | -d }] [-v]",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--endpoint", "-e", type="string", nargs=1, action="store", dest="endpoint",
                                 help="set broker endpoint")

        self.__parser.add_option("--client", "-c", type="string", nargs=1, action="store", dest="client_id",
                                 help="set client ID")

        self.__parser.add_option("--cert", "-i", type="string", nargs=1, action="store", dest="cert_id",
                                 help="set certificate ID")

        self.__parser.add_option("--delete", "-d", action="store_true", dest="delete", default=False,
                                 help="delete the client authentication")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.set() and self.delete:
            return False

        return True


    def is_complete(self):
        if self.endpoint is None or self.client_id is None or self.cert_id is None:
            return False

        return True


    def set(self):
        return self.endpoint is not None or self.client_id is not None or self.cert_id is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def endpoint(self):
        return self.__opts.endpoint


    @property
    def client_id(self):
        return self.__opts.client_id


    @property
    def cert_id(self):
        return self.__opts.cert_id


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def delete(self):
        return self.__opts.delete


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSClientAuth:{endpoint:%s, client_id:%s, cert_id:%s, delete:%s, verbose:%s, args:%s}" % \
               (self.endpoint, self.client_id, self.cert_id, self.delete, self.verbose, self.args)
