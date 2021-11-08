"""
Created on 28 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.data.recurring_period import RecurringMinutes
from scs_core.estate.baseline_conf import BaselineConf
from scs_core.gas.minimum import Minimum


# --------------------------------------------------------------------------------------------------------------------

class CmdBaseline(object):
    """unix command line handler"""

    __UPTAKE_CMDS = ('restart', 'reboot', 'shutdown')

    # --------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        cmds = ' | '.join(self.__UPTAKE_CMDS)

        self.__parser = optparse.OptionParser(usage="%prog [-a] -c NAME -t DEVICE_TAG -f { V | E } "
                                                    "[{ -r | -u COMMAND }] [-s START] [-e END] [-p AGGREGATION] "
                                                    "[-m GAS MINIMUM] [{ -o GAS | -x GAS }] [-v]", version="%prog 1.0")

        # source...
        self.__parser.add_option("--aws", "-a", action="store_true", dest="aws", default=False,
                                 help="Use AWS S3 instead of local storage for configuration")

        # identity...
        self.__parser.add_option("--conf-name", "-c", type="string", nargs=1, action="store", dest="conf_name",
                                 help="the name of the baseline configuration")

        self.__parser.add_option("--device-tag", "-t", type="string", nargs=1, action="store", dest="device_tag",
                                 help="the device to be baselined")

        # function...
        self.__parser.add_option("--fields", "-f", type="string", nargs=1, action="store", dest="fields",
                                 help="baseline Val or Exg fields")

        self.__parser.add_option("--rehearse", "-r", action="store_true", dest="rehearse", default=False,
                                 help="show what actions should be performed")

        self.__parser.add_option("--uptake", "-u", type="string", nargs=1, action="store", dest="uptake",
                                 default="reboot", help="{ %s }, default 'reboot'" % cmds)

        # fields...
        self.__parser.add_option("--start-hour", "-s", type="int", nargs=1, action="store", dest="start_hour",
                                 help="override the configuration's start hour")

        self.__parser.add_option("--end-hour", "-e", type="int", nargs=1, action="store", dest="end_hour",
                                 help="override the configuration's end hour")

        self.__parser.add_option("--aggregation-period", "-p", type="int", nargs=1, action="store",
                                 dest="aggregation_period", help="override the configuration's aggregation period")

        self.__parser.add_option("--minimum", "-m", type="string", nargs=2, action="store", dest="minimum",
                                 help="override configuration's minimum for GAS")

        self.__parser.add_option("--only-gas", "-o", type="string", nargs=1, action="store", dest="only_gas",
                                 help="baseline only GAS")

        self.__parser.add_option("--exclude-gas", "-x", type="string", nargs=1, action="store", dest="exclude_gas",
                                 help="exclude GAS")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.conf_name is None or self.device_tag is None:
            return False

        if self.fields not in Minimum.FIELD_SELECTIONS:
            return False

        if self.uptake not in self.__UPTAKE_CMDS:
            return False

        try:
            _ = self.minimum_value
        except ValueError:
            return False

        if self.only_gas is not None and self.exclude_gas is not None:
            return False

        return True


    def override(self, conf: BaselineConf):
        start_hour = conf.start_hour if self.start_hour is None else self.start_hour
        end_hour = conf.end_hour if self.end_hour is None else self.end_hour
        aggregation_period = conf.aggregation_period if self.aggregation_period is None else \
            RecurringMinutes(self.aggregation_period)

        minimums = {self.only_gas: conf.minimum(self.only_gas)} if self.only_gas else conf.minimums

        conf = BaselineConf(conf.name, conf.timezone, start_hour, end_hour, aggregation_period, minimums)

        if self.minimum_gas is not None:
            conf.set_minimum(self.minimum_gas, self.minimum_value)

        if self.exclude_gas is not None:
            conf.remove_minimum(self.exclude_gas)

        return conf


    def excludes_gas(self, gas):
        return self.only_gas is not None and gas != self.only_gas


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def aws(self):
        return self.__opts.aws


    @property
    def conf_name(self):
        return self.__opts.conf_name


    @property
    def device_tag(self):
        return self.__opts.device_tag


    @property
    def fields(self):
        return self.__opts.fields


    @property
    def rehearse(self):
        return self.__opts.rehearse


    @property
    def uptake(self):
        return self.__opts.uptake


    @property
    def start_hour(self):
        return self.__opts.start_hour


    @property
    def end_hour(self):
        return self.__opts.end_hour


    @property
    def aggregation_period(self):
        return self.__opts.aggregation_period


    @property
    def minimum_gas(self):
        return None if self.__opts.minimum is None else self.__opts.minimum[0]


    @property
    def minimum_value(self):
        return None if self.__opts.minimum is None else int(self.__opts.minimum[1])


    @property
    def only_gas(self):
        return self.__opts.only_gas


    @property
    def exclude_gas(self):
        return self.__opts.exclude_gas


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdBaseline:{aws:%s, conf_name:%s, device_tag:%s, fields:%s, rehearse:%s, uptake:%s, start_hour:%s, " \
               "end_hour:%s, aggregation_period:%s, minimum:%s, only_gas:%s, exclude_gas:%s, " \
               "verbose:%s}" % \
               (self.aws, self.conf_name, self.device_tag, self.fields, self.rehearse, self.uptake, self.start_hour,
                self.end_hour, self.aggregation_period, self.__opts.minimum, self.only_gas, self.exclude_gas,
                self.verbose)
