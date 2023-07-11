"""
Created on 29 Jun 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.data.recurring_period import RecurringPeriod


# --------------------------------------------------------------------------------------------------------------------

class CmdAlert(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS]  { -F | -R ID | -C | -U ID | -D ID } "
                                                    "[-d DESCRIPTION] [-p TOPIC] [-f FIELD] [-l LOWER] [-u UPPER] "
                                                    "[-n { 1 | 0 }] [-a INTERVAL UNITS] [-t INTERVAL] [-j { 1 | 0 }] "
                                                    "[-s { 1 | 0 }] [-i INDENT] [-v] "
                                                    "[-e EMAIL_ADDR] [-g EMAIL_ADDR_1 .. EMAIL_ADDR_N]",
                                              version="%prog 1.0")

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--find", "-F", action="store_true", dest="find", default=False,
                                 help="find alerts for given description, topic, field or email")

        self.__parser.add_option("--retrieve", "-R", type="int", action="store", dest="retrieve_id",
                                 help="retrieve alert with given ID")

        self.__parser.add_option("--create", "-C", action="store_true", dest="create", default=False,
                                 help="create alert")

        self.__parser.add_option("--update", "-U", type="int", action="store", dest="update_id",
                                 help="update alert with given ID")

        self.__parser.add_option("--delete", "-D", type="int", action="store", dest="delete_id",
                                 help="delete alert with given ID")

        # fields...
        self.__parser.add_option("--description", "-d", type="string", action="store", dest="description",
                                 default="", help="description")

        self.__parser.add_option("--topic-path", "-p", type="string", action="store", dest="topic",
                                 help="topic path")

        self.__parser.add_option("--field", "-f", type="string", action="store", dest="field",
                                 help="field")

        self.__parser.add_option("--lower-threshold", "-l", type="float", action="store", dest="lower_threshold",
                                 help="lower threshold")

        self.__parser.add_option("--upper-threshold", "-u", type="float", action="store", dest="upper_threshold",
                                 help="upper threshold")

        self.__parser.add_option("--alert-on-none", "-n", type="int", action="store", dest="alert_on_none",
                                 default=False, help="alert on none (default false)")

        self.__parser.add_option("--aggregation-period", "-a", type="string", nargs=2, action="store",
                                 dest="aggregation_period", help="aggregation interval and units { D | H | M }")

        self.__parser.add_option("--test-interval", "-t", type="string", action="store", dest="test_interval",
                                 help="test interval (NOT IN USE)")

        self.__parser.add_option("--json-message", "-j", type="int", action="store", dest="json_message",
                                 default=None, help="message body is JSON (default false)")

        self.__parser.add_option("--suspended", "-s", type="int", action="store", dest="suspended",
                                 default=None, help="suspended (default false)")

        # email...
        self.__parser.add_option("--email", "-e", type="string", action="store", dest="email",
                                 help="email To address (any on find)")

        self.__parser.add_option("--cc-list", "-g", action="store_true", dest="cc", default=False,
                                 help="email CC list")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", nargs=1, action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.find:
            count += 1

        if self.retrieve:
            count += 1

        if self.create:
            count += 1

        if self.update:
            count += 1

        if self.delete:
            count += 1

        if count != 1:
            return False

        if self.__opts.aggregation_period is not None:
            try:
                int(self.__opts.aggregation_period[0])
            except ValueError:
                return False

        if self.alert_on_none is not None and self.alert_on_none != 0 and self.alert_on_none != 1:
            return False

        if self.json_message is not None and self.json_message != 0 and self.json_message != 1:
            return False

        if self.suspended is not None and self.suspended != 0 and self.suspended != 1:
            return False

        return True


    def is_complete(self):
        if not self.create:
            return True

        if self.topic is None or self.field is None or self.aggregation_period is None:
            return False

        if self.lower_threshold is None and self.upper_threshold is None and not self.alert_on_none:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------
    # properties: identity...

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def id(self):
        if self.__opts.retrieve_id is not None:
            return self.__opts.retrieve_id

        if self.__opts.update_id is not None:
            return self.__opts.update_id

        if self.__opts.delete_id is not None:
            return self.__opts.delete_id

        return None


    # ----------------------------------------------------------------------------------------------------------------
    # properties: operations...

    @property
    def find(self):
        return self.__opts.find


    @property
    def retrieve(self):
        return self.__opts.retrieve_id is not None


    @property
    def create(self):
        return self.__opts.create


    @property
    def update(self):
        return self.__opts.update_id is not None


    @property
    def delete(self):
        return self.__opts.delete_id is not None


    # ----------------------------------------------------------------------------------------------------------------
    # properties: fields...

    @property
    def description(self):
        return self.__opts.description


    @property
    def topic(self):
        return self.__opts.topic


    @property
    def field(self):
        return self.__opts.field


    @property
    def lower_threshold(self):
        return self.__opts.lower_threshold


    @property
    def upper_threshold(self):
        return self.__opts.upper_threshold


    @property
    def alert_on_none(self):
        return self.__opts.alert_on_none


    @property
    def aggregation_period(self):
        period = self.__opts.aggregation_period
        return None if period is None else RecurringPeriod.construct(period[0], period[1])


    @property
    def test_interval(self):
        return self.__opts.test_interval


    @property
    def json_message(self):
        return self.__opts.json_message


    @property
    def suspended(self):
        return self.__opts.suspended


    # ----------------------------------------------------------------------------------------------------------------
    # properties: email...

    @property
    def email(self):
        return self.__opts.email


    @property
    def cc(self):
        return self.__opts.cc


    @property
    def cc_list(self):
        return self.__args if self.cc else None


    # ----------------------------------------------------------------------------------------------------------------
    # fields: output...

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
        return "CmdAlert:{credentials_name:%s, find:%s, retrieve:%s, create:%s, update:%s, " \
               "delete:%s, topic:%s, field:%s, lower_threshold:%s, upper_threshold:%s, " \
               "alert_on_none:%s, aggregation_period:%s, test_interval:%s, json_message:%s, suspended:%s, " \
               "email:%s, cc:%s, cc_list:%s, indent:%s, verbose:%s}" % \
               (self.credentials_name, self.find, self.__opts.retrieve_id, self.create, self.__opts.update_id,
                self.__opts.delete_id, self.topic, self.field, self.lower_threshold, self.upper_threshold,
                self.alert_on_none, self.aggregation_period, self.test_interval, self.json_message, self.suspended,
                self.email, self.cc, self.cc_list, self.indent, self.verbose)
