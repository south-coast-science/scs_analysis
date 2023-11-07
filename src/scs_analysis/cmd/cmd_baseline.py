"""
Created on 28 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_analysis import version

from scs_core.data.diurnal_period import DiurnalPeriod
from scs_core.data.recurring_period import RecurringMinutes

from scs_core.estate.baseline_conf import BaselineConf

from scs_core.gas.minimum import Minimum


# --------------------------------------------------------------------------------------------------------------------

class CmdBaseline(object):
    """unix command line handler"""

    __UPTAKE_CMDS = ('restart', 'reboot', 'shutdown')
    __DEFAULT_UPTAKE_CMD = 'shutdown'

    # --------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        cmds = ' | '.join(self.__UPTAKE_CMDS)

        self.__parser = optparse.OptionParser(usage="%prog [-c CREDENTIALS] -n CONF_NAME -f { V | E } "
                                                    "[{ -r | -u COMMAND }] "
                                                    "[-s START] [-e END] [-p AGGREGATION] [-m GAS MINIMUM] "
                                                    "[{ -o GAS | -x GAS }] [-v] DEVICE_TAG_1 [..DEVICE_TAG_N]",
                                              version=version())

        # identity...
        self.__parser.add_option("--credentials", "-c", type="string", action="store", dest="credentials_name",
                                 help="the stored credentials to be presented")

        # target...
        self.__parser.add_option("--conf-name", "-n", type="string", action="store", dest="conf_name",
                                 help="the name of the baseline configuration")

        # function...
        self.__parser.add_option("--fields", "-f", type="string", action="store", dest="fields",
                                 help="baseline Val or Exg fields")

        self.__parser.add_option("--rehearse", "-r", action="store_true", dest="rehearse", default=False,
                                 help="show what actions should be performed")

        self.__parser.add_option("--uptake", "-u", type="string", action="store", dest="uptake",
                                 default=self.__DEFAULT_UPTAKE_CMD,
                                 help="{ %s } default '%s'" % (cmds, self.__DEFAULT_UPTAKE_CMD))

        # fields...
        self.__parser.add_option("--start", "-s", type="string", action="store", dest="start",
                                 help="override the configuration's start time")

        self.__parser.add_option("--end", "-e", type="string", action="store", dest="end",
                                 help="override the configuration's end time")

        self.__parser.add_option("--aggregation-period", "-p", type="int", action="store",
                                 dest="interval", help="override the configuration's aggregation period")

        self.__parser.add_option("--minimum", "-m", type="string", nargs=2, action="store", dest="minimum",
                                 help="override configuration's minimum for GAS")

        # exclusions...
        self.__parser.add_option("--only-gas", "-o", type="string", action="store", dest="only_gas",
                                 help="baseline only GAS")

        self.__parser.add_option("--exclude-gas", "-x", type="string", action="store", dest="exclude_gas",
                                 help="exclude GAS")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.conf_name is None or len(self.device_tags) < 1:
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

        if not self.__args:
            return False

        return True


    def override(self, conf: BaselineConf):
        start_str = str(conf.sample_period.start_time) if self.start is None else self.start
        end_str = str(conf.sample_period.end_time) if self.end is None else self.end
        sample_period = DiurnalPeriod.construct(start_str, end_str, str(conf.timezone))

        aggregation_period = conf.aggregation_period if self.start is None else \
            RecurringMinutes(self.start, conf.timezone)

        minimums = {self.only_gas: conf.minimum(self.only_gas)} if self.only_gas else conf.minimums

        conf = BaselineConf(conf.name, sample_period, aggregation_period, minimums)

        if self.minimum_gas is not None:
            conf.set_minimum(self.minimum_gas, self.minimum_value)

        if self.exclude_gas is not None:
            conf.remove_minimum(self.exclude_gas)

        return conf


    def excludes_gas(self, gas):
        return self.only_gas is not None and gas != self.only_gas


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def credentials_name(self):
        return self.__opts.credentials_name


    @property
    def conf_name(self):
        return self.__opts.conf_name


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
    def start(self):
        return self.__opts.start


    @property
    def end(self):
        return self.__opts.end


    @property
    def interval(self):
        return self.__opts.interval


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


    @property
    def device_tags(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdBaseline:{credentials_name:%s, conf_name:%s, fields:%s, rehearse:%s, uptake:%s, start:%s, " \
               "end:%s, aggregation_period:%s, minimum:%s, only_gas:%s, exclude_gas:%s, " \
               "verbose:%s, device_tags:%s}" % \
               (self.credentials_name, self.conf_name, self.fields, self.rehearse, self.uptake, self.start,
                self.end, self.interval, self.__opts.minimum, self.only_gas, self.exclude_gas,
                self.verbose, self.device_tags)
