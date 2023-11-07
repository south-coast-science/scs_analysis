"""
Created on 29 Jun 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version

from scs_core.data.diurnal_period import DiurnalPeriod
from scs_core.data.recurring_period import RecurringPeriod

from scs_core.email.email import EmailRecipient

from scs_core.location.timezone import Timezone


# --------------------------------------------------------------------------------------------------------------------

class CmdAlert(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -z | [-c CREDENTIALS]  "
                                                    "{ -F | -R ID | -C | -U ID | -D ID } "
                                                    "[-d DESCRIPTION] [-p TOPIC] [-f FIELD] [-l LOWER] [-u UPPER] "
                                                    "[-n { 0 | 1 }] "
                                                    "[{ -r INTERVAL UNITS TIMEZONE | -t START END TIMEZONE }] "
                                                    "[-a { 0 | 1 }] [-s { 0 | 1 }] [-i INDENT] [-v] "
                                                    "[-e EMAIL_ADDR] [-b { A | R } EMAIL_ADDR [-j]] }",
                                              version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # operations...
        self.__parser.add_option("--zones", "-z", action="store_true", dest="list", default=False,
                                 help="list the available timezone names to stderr")

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

        self.__parser.add_option("--recurring-period", "-r", type="string", nargs=3, action="store",
                                 dest="recurring_period",
                                 help="aggregation interval, units { D | H | M } and timezone")

        self.__parser.add_option("--diurnal-period", "-t", type="string", nargs=3, action="store",
                                 dest="diurnal_period", help="aggregation start, end and timezone")

        self.__parser.add_option("--contiguous-alerts", "-a", type="int", action="store",
                                 dest="contiguous_alerts", default=None,
                                 help="raise alert on contiguous exceedence (default true)")

        self.__parser.add_option("--suspended", "-s", type="int", action="store", dest="suspended",
                                 default=None, help="suspended (default false)")

        # email...
        self.__parser.add_option("--email", "-e", type="string", action="store", dest="email",
                                 help="email To address (any on find)")

        self.__parser.add_option("--bcc-list", "-b", type="string", nargs=2, action="store", dest="bcc", default=False,
                                 help="Add or Remove from BCC list")

        self.__parser.add_option("--json-message", "-j", action="store_true", dest="json_message", default=False,
                                 help="message body is JSON")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.list:
            count += 1

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

        if self.alert_on_none is not None and self.alert_on_none != 0 and self.alert_on_none != 1:
            return False

        if self.json_message is not None and self.json_message != 0 and self.json_message != 1:
            return False

        if self.contiguous_alerts is not None and \
                self.contiguous_alerts != 0 and self.contiguous_alerts != 1:
            return False

        if self.suspended is not None and self.suspended != 0 and self.suspended != 1:
            return False

        if self.bcc and self.bcc_action not in ['A', 'R']:
            return False

        if self.__args:
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


    def is_valid_start_time(self):
        if self.__opts.diurnal_period is None:
            return True

        return DiurnalPeriod.is_valid_time(self.__opts.diurnal_period[0])


    def is_valid_end_time(self):
        if self.__opts.diurnal_period is None:
            return True

        return DiurnalPeriod.is_valid_time(self.__opts.diurnal_period[1])


    def is_valid_timezone(self):
        if self.__opts.recurring_period is not None:
            return Timezone.is_valid(self.__opts.recurring_period[2])

        if self.__opts.diurnal_period is not None:
            return Timezone.is_valid(self.__opts.diurnal_period[2])

        return True


    def updated_bcc_dict(self, existing_bcc_dict):
        if not self.bcc:
            return existing_bcc_dict

        if self.bcc[0] == 'A':
            existing_bcc_dict[self.bcc[1]] = EmailRecipient(self.bcc[1], self.json_message)
            return existing_bcc_dict

        if self.bcc[0] == 'R':
            del existing_bcc_dict[self.bcc[1]]
            return existing_bcc_dict


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
    def list(self):
        return self.__opts.list


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
        return self.diurnal_period if self.recurring_period is None else self.recurring_period


    @property
    def recurring_period(self):
        period = self.__opts.recurring_period
        return None if period is None else RecurringPeriod.construct(period[0], period[1], period[2])


    @property
    def diurnal_period(self):
        period = self.__opts.diurnal_period
        return None if period is None else DiurnalPeriod.construct(period[0], period[1], period[2])


    @property
    def contiguous_alerts(self):
        return self.__opts.contiguous_alerts


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
    def bcc(self):
        return self.__opts.bcc


    @property
    def bcc_action(self):
        return None if not self.__opts.bcc else self.__opts.bcc[0]


    @property
    def bcc_email(self):
        return None if not self.__opts.bcc else self.__opts.bcc[1]


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
        return "CmdAlert:{list:%s, credentials_name:%s, find:%s, retrieve:%s, create:%s, " \
               "update:%s, delete:%s, topic:%s, field:%s, lower_threshold:%s, " \
               "upper_threshold:%s, alert_on_none:%s, recurring_period:%s, diurnal_period:%s, " \
               "json_message:%s, json_message:%s, suspended:%s, email:%s, bcc:%s, " \
               "indent:%s, verbose:%s}" % \
               (self.list, self.credentials_name, self.find, self.__opts.retrieve_id, self.create,
                self.__opts.update_id, self.__opts.delete_id, self.topic, self.field, self.lower_threshold,
                self.upper_threshold, self.alert_on_none, self.__opts.recurring_period, self.__opts.diurnal_period,
                self.contiguous_alerts, self.json_message, self.suspended, self.email, self.bcc,
                self.indent, self.verbose)
