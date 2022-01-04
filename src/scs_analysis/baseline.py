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

The baseline utility requires access_key, aws_api_auth and aws_client_auth to be set.

SYNOPSIS
baseline.py [-a] -c NAME -t DEVICE_TAG -f { V | E } [{ -r | -u COMMAND }] [-s START] [-e END] [-p AGGREGATION]
[-m GAS MINIMUM] [{ -o GAS | -x GAS }] [-v]

EXAMPLES
baseline.py -ac freshfield -t scs-be2-3 -f E -r

FILES
~/SCS/conf/NAME_baseline_conf.json

SEE ALSO
scs_analysis/access_key
scs_analysis/aws_api_auth
scs_analysis/aws_client_auth
scs_analysis/baseline_conf

scs_dev/gases_sampler

scs_mfr/afe_baseline
scs_mfr/gas_baseline
scs_mfr/scd30_baseline
"""

import json

import sys

from scs_analysis.cmd.cmd_baseline import CmdBaseline

from scs_analysis.handler.aws_topic_history_reporter import AWSTopicHistoryReporter

from scs_core.aws.client.access_key import AccessKey
from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.client.client import Client
from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient, MQTTSubscriber

from scs_core.aws.manager.byline_manager import BylineManager
from scs_core.aws.manager.lambda_message_manager import MessageManager
from scs_core.aws.manager.s3_manager import S3PersistenceManager

from scs_core.control.control_handler import ControlHandler

from scs_core.data.datetime import LocalizedDatetime

from scs_core.estate.baseline_conf import BaselineConf
from scs_core.estate.configuration import Configuration
from scs_core.estate.mqtt_peer import MQTTPeerSet

from scs_core.gas.afe_baseline import AFEBaseline
from scs_core.gas.afe_calib import AFECalib
from scs_core.gas.minimum import Minimum

from scs_core.sample.gases_sample import GasesSample

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# TODO: optionally specify a closest datetime for low - in order to synchronise multiple devices
# TODO: review Ox handling
# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    MQTT_TIMEOUT = 60           # seconds

    logger = None
    key = None
    monitor_auth = None
    mqtt_client = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdBaseline()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('baseline', verbose=cmd.verbose)
        logger = Logging.getLogger()


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        # AccessKey (for S3PersistenceManager)...
        if not AccessKey.exists(Host):
            logger.error("AccessKey not available.")
            exit(1)

        try:
            key = AccessKey.load(Host, encryption_key=AccessKey.password_from_user())
        except (KeyError, ValueError):
            logger.error("incorrect password")
            exit(1)

        # APIAuth (for BylineManager)...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            logger.error("APIAuth is not available")
            exit(1)

        # ClientAuth (for MQTTClient)...
        client_auth = ClientAuth.load(Host)

        if client_auth is None:
            logger.error("ClientAuth not available.")
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # S3PersistenceManager...
        s3_client = Client.construct('s3', key)
        s3_resource_client = Client.resource('s3', key)

        s3_manager = S3PersistenceManager(s3_client, s3_resource_client)

        # BylineManager...
        byline_manager = BylineManager(api_auth)

        # reporter...
        reporter = AWSTopicHistoryReporter(cmd.verbose)

        # message manager...
        message_manager = MessageManager(api_auth, reporter=reporter)

        # PersistenceManager...
        persistence_manager = s3_manager if cmd.aws else Host


        # ------------------------------------------------------------------------------------------------------------
        # configuration...

        logger.error("configuration...")

        # BaselineConf...
        baseline_conf = BaselineConf.load(persistence_manager, name=cmd.conf_name)

        if baseline_conf is None:
            logger.error("the BaselineConf '%s' is not available." % cmd.conf_name)
            exit(1)

        try:
            baseline_conf = cmd.override(baseline_conf)
        except KeyError as ex:
            logger.error("the gas %s is not in the baseline configuration." % ex)
            exit(2)

        # host name...
        host_tag = Host.name()

        # topics...
        group = byline_manager.find_bylines_for_device(cmd.device_tag)

        if group is None:
            logger.error("no bylines found for %s." % cmd.device_tag)
            exit(1)

        gases_topic = group.latest_topic('/gases')
        control_topic = group.latest_topic('/control')

        if gases_topic is None:
            logger.error("no gases topic found for %s." % cmd.device_tag)
            exit(1)

        if control_topic is None:
            logger.error("no control topic found for %s." % cmd.device_tag)
            exit(1)

        logger.error("gases_topic: %s" % gases_topic)
        logger.error("control_topic: %s" % control_topic)

        # MQTT peer...
        peer_group = MQTTPeerSet.load(s3_manager)
        peer = peer_group.peer_by_tag(cmd.device_tag)

        if peer is None:
            logger.error("no MQTT peer found for tag '%s'." % cmd.device_tag)
            exit(1)

        logger.error("hostname: %s" % peer.hostname)

        # MQTTClient...
        handler = ControlHandler(host_tag, cmd.device_tag)
        subscriber = MQTTSubscriber(control_topic, handler.handle)

        mqtt_client = MQTTClient(subscriber)
        mqtt_client.connect(client_auth, False)

        # Configuration...
        stdout, stderr = handler.publish(mqtt_client, control_topic, ['configuration'], MQTT_TIMEOUT,
                                         peer.shared_secret)

        if stderr:
            logger.error("Configuration cannot be retrieved: %s" % stderr[0])
            exit(1)

        jdict = json.loads(stdout[0])
        device_conf = Configuration.construct_from_jdict(jdict.get('val'))

        ox_index = None if device_conf.afe_id is None else device_conf.afe_id.sensor_index('Ox')

        # AFECAlib...
        if ox_index is None:
            ox_sensor = None

        else:
            stdout, stderr = handler.publish(mqtt_client, control_topic, ['afe_calib'], MQTT_TIMEOUT,
                                             peer.shared_secret)
            if stderr:
                logger.error("AFECAlib cannot be retrieved: %s" % stderr[0])
                exit(1)

            jdict = json.loads(stdout[0])
            afe_calib = AFECalib.construct_from_jdict(jdict)

            afe_baseline = AFEBaseline.null_datum() if device_conf.afe_baseline is None else device_conf.afe_baseline

            ox_baseline = afe_baseline.sensor_baseline(ox_index)
            ox_calib = afe_calib.sensor_calib(ox_index)

            ox_sensor = ox_calib.sensor(ox_baseline)
            # logger.error(ox_sensor)

        logger.error("-")


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # data...
        logger.error("data...")

        now = LocalizedDatetime.now()

        start = baseline_conf.start_datetime(now)
        end = baseline_conf.end_datetime(now)

        logger.error("start: %s end: %s" % (start, end))

        if start == end:
            logger.error("the start and end hours may not be the same.")
            exit(1)

        if end > now:
            logger.error("baselining cannot take place during the test period.")
            exit(1)

        data = list(message_manager.find_for_topic(gases_topic, start, end, None, False, baseline_conf.checkpoint(),
                                                   False, False, False, False, False, None))
        if not data:
            logger.error("no data found for %s." % gases_topic)
            exit(1)

        logger.error("expected: %s retrieved: %s" % (baseline_conf.expected_data_points(start, end), len(data)))
        logger.error("-")

        # corrections...
        logger.error("correction...")

        conf_minimums = baseline_conf.minimums
        correction_applied = False
        no2_correction = None

        for minimum in Minimum.find_minimums(data, cmd.fields):
            if cmd.excludes_gas(minimum.gas):
                continue

            logger.error("-")

            if minimum.gas == cmd.exclude_gas:
                logger.error("%s is excluded - skipping" % minimum.gas)
                continue

            if minimum.gas not in conf_minimums:
                logger.error("%s has no specified minimum - skipping" % minimum.gas)
                continue

            # NO2...
            if minimum.path == 'val.NO2.cnc':
                no2_correction = conf_minimums['NO2'] - minimum.value

            try:
                if minimum.update_already_done(device_conf, end):
                    logger.error("%s has been updated since the latest test period - skipping" % minimum.path)
                    continue

            except ValueError as ex:
                logger.error("sensor with serial number %s is not supported - skipping" % ex)
                continue

            # Ox...
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

            # minimums...
            if minimum.value == conf_minimums[minimum.gas]:
                logger.error("%s matches the specified minimum - skipping" % minimum.path)
                continue

            if minimum.index == 0:
                logger.error("WARNING: the first datum for %s is the minimum value" % minimum.path)

            elif minimum.index == len(data) - 1:
                logger.error("WARNING: the last datum for %s is the minimum value" % minimum.path)

            # logger.error("acting on: %s" % minimum)
            # logger.error("...")

            cmd_tokens = minimum.cmd_tokens(conf_minimums)
            logger.error(' '.join([str(token) for token in cmd_tokens]))

            if cmd.rehearse:
                continue

            stdout, stderr = handler.publish(mqtt_client, control_topic, cmd_tokens, MQTT_TIMEOUT, peer.shared_secret)
            correction_applied = True

            if stderr:
                print(*stderr, sep='\n', file=sys.stderr)
            if stdout:
                print(*stdout, sep='\n', file=sys.stdout)

        if not correction_applied:
            exit(0)

        logger.error("-")

        # reboot...
        logger.error(cmd.uptake)

        handler.publish(mqtt_client, control_topic, [cmd.uptake], MQTT_TIMEOUT, peer.shared_secret)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except TimeoutError:
        logger.error("device is not available.")
        exit(1)

    finally:
        if mqtt_client:
            mqtt_client.disconnect()
