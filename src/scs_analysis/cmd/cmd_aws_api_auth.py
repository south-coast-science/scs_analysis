"""
Created on 2 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

example document:
{"org-id": "south-coast-science-test-user", "api-key": "9fdfb841-3433-45b8-b223-3f5a283ceb8e"}
"""

import optparse

from scs_airnow import version


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSAPIAuth(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ [-e ENDPOINT] [-a API_KEY] | -d }] [-v]",
                                              version=version())

        # set...
        self.__parser.add_option("--endpoint", "-e", type="string", nargs=1, action="store", dest="endpoint",
                                 help="set API endpoint")

        self.__parser.add_option("--api-key", "-a", type="string", nargs=1, action="store", dest="api_key",
                                 help="set API key")

        self.__parser.add_option("--delete", "-d", action="store_true", dest="delete", default=False,
                                 help="delete the API configuration")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.set() and self.delete:
            return False

        return True


    def is_complete(self):
        if self.endpoint is None or self.api_key is None:
            return False

        return True


    def set(self):
        return self.endpoint is not None or self.api_key is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def endpoint(self):
        return self.__opts.endpoint


    @property
    def api_key(self):
        return self.__opts.api_key


    @property
    def delete(self):
        return self.__opts.delete


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSAPIAuth:{endpoint:%s, api_key:%s, delete:%s, verbose:%s}" % \
               (self.endpoint, self.api_key, self.delete, self.verbose)
