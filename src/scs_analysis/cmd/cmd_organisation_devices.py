"""
Created on 19 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdOrganisationDevices(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] { -F { -l ORG_LABEL | -t DEVICE_TAG } | "
                                                    "-C -l ORG_LABEL -t DEVICE_TAG -p PATH_ROOT GROUP LOCATION"
                                                    " -d DEPLOYMENT_LABEL | -D -t DEVICE_TAG } "
                                                    "[-i INDENT] [-v]", version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--Find", "-F", action="store_true", dest="find", default=False,
                                 help="find devices for the organisation or device tag")

        self.__parser.add_option("--Create", "-C", action="store_true", dest="create", default=False,
                                 help="create a device")

        self.__parser.add_option("--Delete", "-D", action="store_true", dest="delete", default=False,
                                 help="delete the device")

        # fields...
        self.__parser.add_option("--org-label", "-l", type="string", action="store", dest="org_label",
                                 help="the organisation label")

        self.__parser.add_option("--device-tag", "-t", type="string", action="store", dest="device_tag",
                                 help="the device tag")

        self.__parser.add_option("--project", "-p", type="string", nargs=3, action="store", dest="project",
                                 help="path root, group and location number")

        self.__parser.add_option("--deployment-label", "-d", type="string", action="store", dest="deployment_label",
                                 help="the device's deployment label")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.find:
            count += 1

        if self.create:
            count += 1

        if self.delete:
            count += 1

        if count != 1:
            return False

        if self.find and self.org_label is None and self.device_tag is None:
            return False

        if (self.create or self.delete) and (self.org_label is None or self.device_tag is None):
            return False

        if self.delete and (self.__opts.project is None):
            return False

        if self.create and (self.__opts.project is None or self.deployment_label is None):
            return False

        if self.__args:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def find(self):
        return self.__opts.find


    @property
    def create(self):
        return self.__opts.create


    @property
    def delete(self):
        return self.__opts.delete


    @property
    def org_label(self):
        return self.__opts.org_label


    @property
    def device_tag(self):
        return self.__opts.device_tag


    @property
    def project_organisation(self):
        return None if self.__opts.project is None else self.__opts.project[0]


    @property
    def project_group(self):
        return None if self.__opts.project is None else self.__opts.project[1]


    @property
    def project_location(self):
        return None if self.__opts.project is None else self.__opts.project[2]


    @property
    def deployment_label(self):
        return self.__opts.deployment_label


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
        return "CmdOrganisationDevices:{credentials_name:%s, find:%s, create:%s, delete:%s, " \
               "org_label:%s, device_tag:%s, project:%s, deployment_label:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.find, self.create, self.delete,
                self.org_label, self.device_tag, self.__opts.project, self.deployment_label, self.indent, self.verbose)
