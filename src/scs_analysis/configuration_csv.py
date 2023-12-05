#!/usr/bin/env python3

"""
Created on 7 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_monitor utility is used to download configuration information from all devices accessible to the
user, and render this in CSV form. Four modes are available:

* --separate - download the latest configuration for all devices, and save this to separate CSV files, each named
for a node. Any nodes specified on the command line are ignored.

* --latest - download the latest configuration for all devices, and save this in the named CSV file.

* --diff-histories - download the history of configuration changes for all devices. Where there has been at least one
change in the configuration for each device, save the history files in the named directory.

* --full-histories - download the history of all configuration changes for all devices.

Nodes are any of:

hostname, packs, afe-baseline, afe-id, aws-api-auth, aws-client-auth, aws-group-config, aws-project, csv-logger-conf,
display-conf, gas-baseline, gas-model-conf, gps-conf, interface-conf, greengrass-identity, mpl115a2-calib, mqtt-conf,
ndir-conf, opc-conf, pmx-model-conf, pressure-conf, psu-conf, psu-version, pt1000-calib, scd30-baseline, scd30-conf,
schedule, shared-secret, sht-conf, sht-conf, networks, modem, sim, system-id, timezone-conf

For separate and latest modes, two rec values are included:

* rec.report - the most recent time that the device reported its status

* rec.update - the most recent time that at least one of the fields changed value (not that those fields might not
be included in the CSV file)

For diff-histories and full-histories modes, a single rec value is included, equivalent to rec.update.

Output CSV cell values are always wrapped in quotes ('"').

SYNOPSIS
configuration_csv.py [-c CREDENTIALS] { -n | -s | -l OUTPUT_CSV | { -d | -f } [-o OUTPUT_CSV_DIR] }
[-t DEVICE_TAG [-x]] [-v] [NODE_1..NODE_N]

EXAMPLES
configuration_csv.py -vs configs.csv
configuration_csv.py -vdo afe_ids afe-id
configuration_csv.py -vft scs-bgx-431

SEE ALSO
scs_analysis/configuration_monitor
scs_analysis/configuration_monitor_check
scs_analysis/monitor_auth

scs_mfr/configuration
"""

import os
import sys

from scs_analysis.cmd.cmd_configuration_csv import CmdConfigurationCSV
from scs_analysis.handler.batch_download_reporter import BatchDownloadReporter
from scs_analysis.handler.configuration_csv_generator import ConfigurationCSVGenerator

from scs_core.aws.manager.configuration.configuration_finder import ConfigurationFinder
from scs_core.aws.manager.configuration.configuration_intercourse import ConfigurationRequest

from scs_core.aws.manager.configuration.configuration_check_finder import ConfigurationCheckFinder
from scs_core.aws.manager.configuration.configuration_check_intercourse import ConfigurationCheckRequest

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException

from scs_core.estate.configuration import Configuration

from scs_core.sample.configuration_sample import ConfigurationReport

from scs_core.sys.filesystem import Filesystem
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    configuration = Configuration.construct_from_jdict(None, skeleton=True)
    node_names = sorted(list(configuration.as_json().keys()))

    logger = None
    configs = []

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdConfigurationCSV()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('configuration_csv', verbose=cmd.verbose)     # verbose=cmd.verbose | level=logging.DEBUG
        logger = Logging.getLogger()

        for node in cmd.nodes:
            if node not in node_names:
                logger.error('nodes must be in: %s' % str(node_names))
                exit(2)

        logger.info(cmd)


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
        # resources...

        # nodes...
        if cmd.node_names:
            print(node_names, file=sys.stderr)
            exit(0)

        # reporter...
        reporter = BatchDownloadReporter()

        # ConfigurationFinder...
        configuration_finder = ConfigurationFinder(reporter=reporter)
        check_finder = ConfigurationCheckFinder()

        # ConfigurationCSVGenerator...
        csv_generator = ConfigurationCSVGenerator(cmd.verbose)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        logger.info("retrieving check reports...")
        checks = check_finder.find(auth.id_token, None, None, ConfigurationCheckRequest.Mode.FULL)
        check_reports = {check.tag: check.rec for check in checks.items}

        if cmd.separate or cmd.latest:
            logger.info("retrieving configurations...")
            response = configuration_finder.find(auth.id_token, cmd.device_tag, cmd.exact_match, cmd.request_mode())
            configs = [ConfigurationReport.construct(item, check_reports[item.tag]) for item in sorted(response)]

        if cmd.separate:
            for node in node_names:
                path = node + '.csv'
                logger.info("-")
                logger.info(path)

                csv_generator.generate(configs, [node], path)

        if cmd.latest:
            logger.info(cmd.latest)
            csv_generator.generate(configs, cmd.nodes, cmd.latest)

        if cmd.diff_histories or cmd.full_histories:
            if cmd.output_csv_dir is not None:
                Filesystem.mkdir(cmd.output_csv_dir)

            logger.info("retrieving device tags...")
            tag_response = configuration_finder.find(auth.id_token, cmd.device_tag, cmd.exact_match,
                                                     ConfigurationRequest.Mode.TAGS_ONLY)

            for tag in sorted(tag_response):
                filename = tag + '-configs.csv'
                path = filename if cmd.output_csv_dir is None else os.path.join(cmd.output_csv_dir, filename)

                logger.info("-")
                logger.info(path)

                response = configuration_finder.find(auth.id_token, tag, True, cmd.request_mode())
                configs = sorted(response)

                csv_generator.generate(configs, cmd.nodes, path)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
