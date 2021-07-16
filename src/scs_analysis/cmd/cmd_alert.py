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
        self.__parser = optparse.OptionParser(usage="%prog  { -f TOPIC | -r ID | -c | -u ID | -d ID } "
                                                    "[-o TOPIC] [-e FIELD] [-l LOWER] [-p UPPER] "
                                                    "[-n { 1 | 0 }] [-a INTERVAL UNITS] [-t INTERVAL] [-s { 1 | 0 }] "
                                                    "[-m EMAIL_ADDR] [-x EMAIL_ADDR] [-i INDENT] [-v]",
                                              version="%prog 1.0")

        # operations...
        self.__parser.add_option("--find", "-f", type="string", action="store", dest="find_topic",
                                 help="find alerts for given TOPIC (and FIELD)")

        self.__parser.add_option("--retrieve", "-r", type="int", action="store", dest="retrieve_id",
                                 help="retrieve alert with given ID")

        self.__parser.add_option("--create", "-c", action="store_true", dest="create", default=False,
                                 help="create alert")

        self.__parser.add_option("--update", "-u", type="int", action="store", dest="update_id",
                                 help="update alert with given ID")

        self.__parser.add_option("--delete", "-d", type="int", action="store", dest="delete_id",
                                 help="delete alert with given ID")

        # fields...
        self.__parser.add_option("--topic-path", "-o", type="string", action="store", dest="topic",
                                 help="topic path")

        self.__parser.add_option("--field", "-e", type="string", action="store", dest="field",
                                 help="field")

        self.__parser.add_option("--lower-threshold", "-l", type="float", action="store", dest="lower_threshold",
                                 help="lower threshold")

        self.__parser.add_option("--upper-threshold", "-p", type="float", action="store", dest="upper_threshold",
                                 help="upper threshold")

        self.__parser.add_option("--alert-on-none", "-n", type="int", action="store", dest="alert_on_none",
                                 default=False, help="alert on none (default false)")

        self.__parser.add_option("--aggregation-period", "-a", type="string", nargs=2, action="store",
                                 dest="aggregation_period", help="aggregation interval and units { D | H | M }")

        self.__parser.add_option("--test-interval", "-t", type="string", action="store", dest="test_interval",
                                 help="test interval")

        self.__parser.add_option("--suspended", "-s", type="int", action="store", dest="suspended",
                                 default=False, help="suspended (default false)")

        # email cc...
        self.__parser.add_option("--add-cc", "-m", type="string", action="store", dest="add_cc",
                                 help="add CC email address")

        self.__parser.add_option("--remove-cc", "-x", type="string", action="store", dest="remove_cc",
                                 help="remove CC email address")

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

    @property
    def find_topic(self):
        return self.__opts.find_topic


    @property
    def find(self):
        return self.__opts.find_topic is not None


    @property
    def retrieve_id(self):
        return self.__opts.retrieve_id


    @property
    def retrieve(self):
        return self.__opts.retrieve_id is not None


    @property
    def create(self):
        return self.__opts.create


    @property
    def update_id(self):
        return self.__opts.update_id


    @property
    def update(self):
        return self.__opts.update_id is not None


    @property
    def delete_id(self):
        return self.__opts.delete_id


    @property
    def delete(self):
        return self.__opts.delete_id is not None


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
    def suspended(self):
        return self.__opts.suspended


    @property
    def add_cc(self):
        return self.__opts.add_cc


    @property
    def remove_cc(self):
        return self.__opts.remove_cc


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
        return "CmdAlert:{find:%s, retrieve:%s, create:%s, update:%s, delete:%s, topic:%s, field:%s, " \
               "lower_threshold:%s, upper_threshold:%s, alert_on_none:%s, aggregation_period:%s, " \
               "test_interval:%s, suspended:%s, add_cc:%s, remove_cc:%s, indent:%s, verbose:%s}" % \
               (self.find_topic, self.retrieve_id, self.create, self.update_id, self.delete_id, self.topic, self.field,
                self.lower_threshold, self.upper_threshold, self.alert_on_none, self.aggregation_period,
                self.test_interval, self.suspended, self.add_cc, self.remove_cc, self.indent, self.verbose)