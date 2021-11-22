#!/usr/bin/env python3

"""
Created on 31 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The baseline_conf utility is used to specify the operating parameters of the baseline utility.

Aggregation periods must be whole divisors of one hour, i.e. 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, or 30 minutes.

Note that if the start time is a later hour than the end time, then the start time is interpreted as that hour
on the previous day.

Any number of separate baseline_conf files may be stored. The --list flag lists those that are available.

SYNOPSIS
baseline_conf.py [-a] { -z | -l | -c NAME [-t TIMEZONE_NAME] [-s START] [-e END] [-p AGGREGATION]
[-g GAS MINIMUM] [-r GAS] } [-i INDENT] [-v]

EXAMPLES
./baseline_conf.py -c freshfield -t Europe/London -s 23 -e 8 -a 5 -g NO2 10

DOCUMENT EXAMPLE
{"timezone": "Europe/London", "start-hour": 17, "end-hour": 8, "aggregation-period": {"interval": 5, "units": "M"},
"gas-minimums": {"CO": 200, "CO2": 420, "H2S": 5, "NO": 10, "NO2": 10, "SO2": 5}}

FILES
~/SCS/conf/NAME_baseline_conf.json

SEE ALSO
scs_analysis/baseline
scs_dev/gases_sampler
"""

import sys

from scs_analysis.cmd.cmd_baseline_conf import CmdBaselineConf

from scs_core.aws.client.access_key import AccessKey
from scs_core.aws.client.client import Client
from scs_core.aws.manager.s3_manager import S3PersistenceManager

from scs_core.data.json import JSONify
from scs_core.data.recurring_period import RecurringMinutes

from scs_core.estate.baseline_conf import BaselineConf

from scs_core.location.timezone import Timezone

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    conf = None
    key = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdBaselineConf()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('baseline_conf', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # PersistenceManager...
    if cmd.aws:
        if not AccessKey.exists(Host):
            logger.error('AccessKey not available.')
            exit(1)

        try:
            key = AccessKey.load(Host, encryption_key=AccessKey.password_from_user())
        except (KeyError, ValueError):
            logger.error('incorrect password.')
            exit(1)

        client = Client.construct('s3', key)
        resource_client = Client.resource('s3', key)

        persistence_manager = S3PersistenceManager(client, resource_client)

    else:
        persistence_manager = Host

    # GasModelConf...
    if not cmd.duplicate():
        conf = BaselineConf.load(persistence_manager, name=cmd.conf_name)


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    if cmd.zones:
        for zone in Timezone.zones():
            print(zone, file=sys.stderr)
        exit(0)

    if cmd.list:
        for conf_name in BaselineConf.list(persistence_manager):
            print(conf_name, file=sys.stderr)
        exit(0)

    if cmd.duplicate():
        source = BaselineConf.load(persistence_manager, name=cmd.duplicate_from)

        if source is None:
            logger.error("no configuration found for '%s'" % cmd.duplicate_from)
            exit(2)

        conf = source.duplicate(cmd.duplicate_to)
        conf.save(persistence_manager)

    if cmd.set():
        if conf is None and not cmd.is_complete():
            logger.error("no configuration is stored - you must therefore set all fields.")
            exit(2)

        if cmd.timezone and not Timezone.is_valid(cmd.timezone):
            logger.error("unrecognised timezone name: %s." % cmd.timezone)
            exit(2)

        if cmd.aggregation_period and cmd.aggregation_period not in RecurringMinutes.valid_intervals():
            logger.error("aggregation period must be one of: %s." % str(RecurringMinutes.valid_intervals()))
            exit(2)

        timezone = conf.timezone if cmd.timezone is None else cmd.timezone
        start_hour = conf.start_hour if cmd.start_hour is None else cmd.start_hour
        end_hour = conf.end_hour if cmd.end_hour is None else cmd.end_hour
        aggregation_period = conf.aggregation_period if cmd.aggregation_period is None else \
            RecurringMinutes(cmd.aggregation_period)

        if start_hour == end_hour:
            logger.error("the start and end hours may not be the same.")
            exit(2)

        minimums = {} if conf is None else conf.minimums

        conf = BaselineConf(cmd.conf_name, timezone, start_hour, end_hour, aggregation_period, minimums)

        if cmd.set_gas_name:
            if cmd.set_gas_name not in BaselineConf.supported_gases():
                logger.error("the gas '%s' is not supported." % cmd.set_gas_name)
                exit(2)

            conf.set_minimum(cmd.set_gas_name, cmd.set_gas_minimum)

        if cmd.remove_gas:
            conf.remove_minimum(cmd.remove_gas)

        conf.save(persistence_manager)

    if conf:
        print(JSONify.dumps(conf, indent=cmd.indent))
