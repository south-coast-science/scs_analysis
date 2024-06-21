#!/usr/bin/env python3

"""
Created on 28 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The baseline utility is use to set the baseline of a device's electrochemical and CO2 sensors according to estimated
low environmental gas concentrations. It does this by downloading device data, finding minimums, then adjusting the
device's baseline offsets by the difference between the estimated and reported values. Any changes in NO2
baselines are incorporated into O3 ('Ox') baselining.

Baselining can be applied to either:

* Val fields - including val.GGG.cnc and val.GGG.vCal (the model inputs)
* Exg fields - of the form exg.val.GGG.cnc or exg.MMM.GGG.cnc (the model outputs)

The device must be online during the baselining operation - a number of MQTT messages are passes between the
utility and the device. If any changes are made to the device's baseline settings, then the gases_sampler process
is restarted. How the restart happens is specified by the --uptake flag.

If the --rehearse flag is used, the baseline utility shows what changes would be made, but does not make the changes.

Operating parameters are specified by the baseline_conf utility, and may be overridden by the baseline utility flags.
Any number of named baseline_conf files may be stored.

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
Usage: baseline.py [-c CREDENTIALS] -n CONF_NAME -f { V | E } [{ -r | -u COMMAND }] [-s START] [-e END]
[-p AGGREGATION] [-m GAS MINIMUM] [{ -o GAS | -x GAS }] [-v] DEVICE_TAG_1 .. DEVICE_TAG_N

EXAMPLES
baseline.py -c super -n freshfield -e 07:00 -fV scs-bgb-410

FILES
~/SCS/conf/baseline_conf/NAME_baseline_conf.json

SEE ALSO
scs_analysis/baseline_conf
scs_analysis/cognito_user_credentials

scs_dev/gases_sampler

scs_mfr/afe_baseline
scs_mfr/gas_baseline
scs_mfr/scd30_baseline
"""

import json
import sys

from scs_analysis.cmd.cmd_baseline import CmdBaseline

from scs_analysis.handler.batch_download_reporter import BatchDownloadReporter

from scs_core.aws.client.device_control_client import DeviceControlClient

from scs_core.aws.manager.byline.byline_finder import BylineFinder
from scs_core.aws.manager.topic_history.topic_history_finder import TopicHistoryFinder

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPGatewayTimeoutException

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.diurnal_period import DiurnalPeriod
from scs_core.data.json import JSONify
from scs_core.data.timedelta import Timedelta

from scs_core.estate.baseline_conf import BaselineConf
from scs_core.estate.configuration import Configuration

from scs_core.gas.afe_baseline import AFEBaseline
from scs_core.gas.afe_calib import AFECalib
from scs_core.gas.minimum import Minimum

from scs_core.sample.gases_sample import GasesSample

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# TODO: review Ox handling
# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    MQTT_TIMEOUT = 60           # seconds

    key = None
    monitor_auth = None
    mqtt_client = None

    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdBaseline()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('baseline', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        credentials = CognitoClientCredentials.load_for_user(Host, name=cmd.credentials_name)

        if not credentials:
            exit(1)

        gatekeeper = CognitoLoginManager()
        auth = gatekeeper.user_login(credentials)

        if not auth.is_ok():
            logger.error("login: %s." % auth.authentication_status.description)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        if cmd.start is not None and not DiurnalPeriod.is_valid_time(cmd.start):
            logger.error("the start time is invalid.")
            exit(2)

        if cmd.end is not None and not DiurnalPeriod.is_valid_time(cmd.end):
            logger.error("the end time is invalid.")
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # BylineFinder...
        byline_finder = BylineFinder(reporter=BatchDownloadReporter('bylines'))

        # MessageManager...
        history_finder = TopicHistoryFinder(reporter=BatchDownloadReporter('history'))

        # DeviceControlClient...
        client = DeviceControlClient()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for device_tag in cmd.device_tags:
            logger.info("-")
            logger.info("device: %s" % device_tag)

            try:
                device_updates = 0

                # ----------------------------------------------------------------------------------------------------
                # configuration...

                logger.info("configuration...")

                # BaselineConf...
                baseline_conf = BaselineConf.load(Host, name=cmd.conf_name)

                if baseline_conf is None:
                    logger.error("the baseline configuration '%s' is not available." % cmd.conf_name)
                    continue

                try:
                    baseline_conf = cmd.override(baseline_conf)
                except KeyError as ex:
                    logger.error("the gas %s is not in the baseline configuration." % ex)
                    continue

                # host name...
                host_tag = Host.name()

                # topics...
                group = byline_finder.find_bylines_for_device(auth.id_token, device_tag)

                if not group:
                    logger.error("no bylines found for %s." % device_tag)
                    continue

                gases_topic = group.latest_topic(suffix='/gases')
                control_topic = group.latest_topic(suffix='/control')

                if gases_topic is None:
                    logger.error("no gases topic found for %s." % device_tag)
                    continue

                if control_topic is None:
                    logger.error("no control topic found for %s." % device_tag)
                    continue

                logger.info("gases_topic: %s" % gases_topic)
                logger.info("control_topic: %s" % control_topic)

                # configuration...
                response = client.interact(auth.id_token, device_tag, ['configuration'])
                command = response.command

                if command.return_code != 0:
                    logger.error("configuration cannot be retrieved: %s" % command.stderr[0])
                    continue

                jdict = json.loads(command.stdout[0])
                device_conf = Configuration.construct_from_jdict(jdict.get('val'))

                # noinspection PyUnresolvedReferences
                ox_index = None if device_conf.afe_id is None else device_conf.afe_id.sensor_index('Ox')

                # AFECalib...
                if ox_index is None:
                    ox_sensor = None

                else:
                    response = client.interact(auth.id_token, device_tag, ['afe_calib'])
                    command = response.command

                    if command.return_code != 0:
                        logger.error("AFECAlib cannot be retrieved: %s" % command.stderr[0])
                        continue

                    jdict = json.loads(command.stdout[0])
                    afe_calib = AFECalib.construct_from_jdict(jdict)

                    afe_baseline = AFEBaseline.null_datum() if device_conf.afe_baseline is None else \
                        device_conf.afe_baseline

                    ox_baseline = afe_baseline.sensor_baseline(ox_index)
                    ox_calib = afe_calib.sensor_calib(ox_index)

                    ox_sensor = ox_calib.sensor(ox_baseline)
                    # logger.error(ox_sensor)

                logger.error("-")


                # ----------------------------------------------------------------------------------------------------
                # analysis...

                # data...
                logger.info("data...")

                now = LocalizedDatetime.now()

                start = baseline_conf.start_datetime(now)
                end = baseline_conf.end_datetime(now)

                if start == end:
                    logger.error("the start and end hours may not be the same.")
                    exit(1)

                if end > now:
                    start -= Timedelta(days=1)
                    end -= Timedelta(days=1)
                    logger.error("WARNING: testing previous day...")

                logger.info("start: %s end: %s" % (start.as_iso8601(), end.as_iso8601()))

                data = list(history_finder.find_for_topic(auth.id_token, gases_topic, start, end,
                                                          None, False, baseline_conf.checkpoint(),
                                                          False, False, False, False, False, None))

                if not data:
                    logger.error("no data found for %s." % gases_topic)
                    continue

                logger.info("expected: %s retrieved: %s" % (baseline_conf.expected_data_points(start, end), len(data)))
                logger.info("-")

                # corrections...
                logger.info("correction...")

                conf_minimums = baseline_conf.minimums
                correction_applied = False
                no2_correction = None

                for minimum in Minimum.find_minimums(data, cmd.fields):
                    gas = minimum.gas

                    if cmd.excludes_gas(gas):       # not "only this gas"
                        continue

                    logger.info("-")
                    logger.info("%s..." % minimum.path)

                    if gas == cmd.exclude_gas:      # is excluded gas
                        logger.error("%s is excluded - skipping" % gas)
                        continue

                    if gas not in conf_minimums:
                        logger.error("%s has no specified minimum - skipping" % gas)
                        continue

                    # NO2...
                    if minimum.path == 'val.NO2.cnc':
                        no2_correction = conf_minimums['NO2'] - minimum.value

                    try:
                        if 'vCal' not in minimum.path and minimum.update_already_done(device_conf, end):
                            logger.error("%s has been updated since the latest test period - skipping" % minimum.path)
                            continue

                    except ValueError as ex:
                        logger.error("sensor with serial number %s is not supported - skipping" % ex)
                        continue

                    # Ox...
                    # TODO: correction needs to happen on the big data set - before minimums are found?
                    if minimum.path == 'val.Ox.cnc':
                        if no2_correction is None:
                            logger.error('NO2 minimum required for Ox, but none available - skipping')
                            continue

                        sample = GasesSample.construct_from_jdict(minimum.sample)

                        temp = sample.sht_datum.temp
                        no2_sample = sample.electrochem_datum.sns['NO2']
                        ox_sample = sample.electrochem_datum.sns['Ox']

                        no2_cnc = no2_sample.cnc + no2_correction
                        corrected = ox_sensor.datum(temp, ox_sample.we_v, ox_sample.ae_v, no2_cnc=no2_cnc)
                        minimum.value = corrected.cnc

                    # report...
                    print(JSONify.dumps(minimum.summary(gas)))
                    sys.stdout.flush()

                    # minimums...
                    if minimum.value == conf_minimums[gas]:
                        logger.error("%s matches the specified minimum - skipping" % minimum.path)
                        continue

                    if minimum.index == 0:
                        logger.error("WARNING: the first datum for %s is the minimum value" % minimum.path)

                    elif minimum.index == len(data) - 1:
                        logger.error("WARNING: the last datum for %s is the minimum value" % minimum.path)


                    # ------------------------------------------------------------------------------------------------
                    # update...

                    cmd_tokens = minimum.cmd_tokens(conf_minimums)
                    logger.info(' '.join([str(token) for token in cmd_tokens]))

                    if cmd.rehearse:
                        continue

                    response = client.interact(auth.id_token, device_tag, cmd_tokens)
                    command = response.command

                    if command.stderr:
                        print(*command.stderr, sep='\n', file=sys.stderr)
                    if command.stdout:
                        print(*command.stdout, sep='\n', file=sys.stdout)

                    if command.return_code != 0:
                        logger.error("update could not be performed: %s" % command.stderr[0])
                        continue

                    device_updates += 1

                # if not device_updates:
                #     continue

                # reboot...
                logger.info("-")

                logger.info(cmd.uptake)

                client.interact(auth.id_token, device_tag, [cmd.uptake])

            except HTTPGatewayTimeoutException:
                logger.error("device '%s' is not available." % device_tag)
                continue

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        logger.info("devices: %d processed: %d" % (len(cmd.device_tags), processed_count))
