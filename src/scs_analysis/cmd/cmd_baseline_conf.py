"""
Created on 31 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version


# --------------------------------------------------------------------------------------------------------------------

class CmdBaselineConf(object):
    """
    unix command line handler
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.__parser = optparse.OptionParser(usage="%prog [-a] { -z | -l | -d FROM TO | -n NAME "
                                                    "[-s START] [-e END] [-p AGGREGATION] [-t TIMEZONE] "
                                                    "[-g GAS MINIMUM] [-r GAS] } "
                                                    "[-i INDENT] [-v]", version=version())

        # source...
        self.__parser.add_option("--aws", "-a", action="store_true", dest="aws", default=False,
                                 help="Use AWS S3 instead of local storage for configuration")

        # helpers...
        self.__parser.add_option("--zones", "-z", action="store_true", dest="zones", default=False,
                                 help="list the available timezone names to stderr")

        self.__parser.add_option("--list", "-l", action="store_true", dest="list", default=False,
                                 help="list the available baseline configurations")

        # identity...
        self.__parser.add_option("--duplicate", "-d", type="string", nargs=2, action="store", dest="duplicate",
                                 help="create a new configuration based on FROM")

        self.__parser.add_option("--conf-name", "-n", type="string", action="store", dest="conf_name",
                                 help="the name of the baseline configuration")

        # fields...
        self.__parser.add_option("--start", "-s", type="string", action="store", dest="start",
                                 help="start of test period")

        self.__parser.add_option("--end", "-e", type="string", action="store", dest="end",
                                 help="end of test period")

        self.__parser.add_option("--aggregation-period", "-p", type="int", action="store",
                                 dest="interval", help="aggregation in minutes")

        self.__parser.add_option("--timezone", "-t", type="string", action="store", dest="timezone",
                                 help="set the timezone for the tests")

        self.__parser.add_option("--set-gas", "-g", type="string", nargs=2, action="store", dest="set_gas",
                                 help="set minimum for GAS")

        self.__parser.add_option("--remove-gas", "-r", type="string", action="store", dest="remove_gas",
                                 help="remove GAS from minimums")

        # output...
        self.__parser.add_option("--indent", "-i", type="int", action="store", dest="indent",
                                 help="pretty-print the output with INDENT")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        count = 0

        if self.zones:
            count += 1

        if self.list:
            count += 1

        if self.duplicate_from is not None:
            count += 1

        if self.conf_name is not None:
            count += 1

        if count != 1:
            return False

        try:
            _ = self.set_gas_minimum
        except ValueError:
            return False

        if self.__args:
            return False

        return True


    def is_complete(self):
        if self.start is None or self.end is None or self.timezone is None or \
                self.interval is None:
            return False

        return True


    def duplicate(self):
        return self.__opts.duplicate is not None


    def set(self):
        return self.start is not None or self.end is not None or self.interval is not None or \
            self.timezone is not None or self.__opts.set_gas is not None or self.remove_gas is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def aws(self):
        return self.__opts.aws


    @property
    def zones(self):
        return self.__opts.zones


    @property
    def list(self):
        return self.__opts.list


    @property
    def duplicate_from(self):
        return self.__opts.duplicate[0] if self.__opts.duplicate else None


    @property
    def duplicate_to(self):
        return self.__opts.duplicate[1] if self.__opts.duplicate else None


    @property
    def conf_name(self):
        return self.__opts.conf_name


    @property
    def start(self):
        return self.__opts.start


    @property
    def end(self):
        return self.__opts.end


    @property
    def interval(self):
        return self.__opts.interval


    @property
    def timezone(self):
        return self.__opts.timezone


    @property
    def set_gas_name(self):
        return None if self.__opts.set_gas is None else self.__opts.set_gas[0]


    @property
    def set_gas_minimum(self):
        return None if self.__opts.set_gas is None else int(self.__opts.set_gas[1])


    @property
    def remove_gas(self):
        return self.__opts.remove_gas


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
        return "CmdBaselineConf:{aws:%s, zones:%s, list:%s, list:%s, conf_name:%s, start:%s, end:%s, " \
               "interval:%s, timezone:%s, set_gas:%s, remove_gas:%s, indent:%s, verbose:%s}" % \
               (self.aws, self.zones, self.list, self.__opts.duplicate, self.conf_name, self.start, self.end,
                self.interval, self.timezone, self.__opts.set_gas, self.remove_gas, self.indent, self.verbose)
