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

Nodes are:

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
configuration_csv.py { -n | -s | -l LATEST_CSV | { -d | -f } HISTORIES_CSV_DIR } [-v] [NODE_1..NODE_N]

EXAMPLES
configuration_csv.py -vl configs.csv

SEE ALSO
scs_analysis/configuration_monitor
scs_analysis/configuration_monitor_check
scs_analysis/monitor_auth

scs_mfr/configuration
"""

import os
import requests
import sys

from subprocess import Popen, PIPE

from scs_analysis.cmd.cmd_configuration_csv import CmdConfigurationCSV

from scs_core.aws.client.monitor_auth import MonitorAuth
from scs_core.aws.manager.configuration_check_finder import ConfigurationCheckFinder, ConfigurationCheckRequest
from scs_core.aws.manager.configuration_finder import ConfigurationFinder, ConfigurationRequest

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

from scs_core.estate.configuration import Configuration

from scs_core.sample.configuration_sample import ConfigurationReport

from scs_core.sys.filesystem import Filesystem
from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

COMMON_NODES = ['tag', 'rec', 'rec.report', 'rec.update', 'ver']    # either rec or rec... depending on document type


# --------------------------------------------------------------------------------------------------------------------

def generate_csv(selected_configs, selected_nodes, file_path):
    jstr = '\n'.join([JSONify.dumps(config) for config in selected_configs])
    node_args = COMMON_NODES + ['val.' + selected_node for selected_node in selected_nodes]

    if selected_nodes:
        p = Popen(['node.py', node_opts] + node_args, stdin=PIPE, stdout=PIPE)
        csv_data, _ = p.communicate(input=jstr.encode())
    else:
        csv_data = jstr.encode()

    p = Popen(['csv_writer.py', csv_opts, file_path], stdin=PIPE)
    p.communicate(input=csv_data)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    configuration = Configuration.construct_from_jdict(None, skeleton=True)
    node_names = sorted(list(configuration.as_json().keys()))

    logger = None
    auth = None
    configs = []

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdConfigurationCSV()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('configuration_csv', verbose=cmd.verbose)
        logger = Logging.getLogger()

        for node in cmd.nodes:
            if node not in node_names:
                logger.error('nodes must be in: %s' % str(node_names))
                exit(2)

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if cmd.node_names:
            print(node_names, file=sys.stderr)
            exit(0)

        if not MonitorAuth.exists(Host):
            logger.error('MonitorAuth not available.')
            exit(1)

        try:
            auth = MonitorAuth.load(Host, encryption_key=MonitorAuth.password_from_user())
        except (KeyError, ValueError):
            logger.error('incorrect password.')
            exit(1)

        configuration_finder = ConfigurationFinder(requests, auth)
        check_finder = ConfigurationCheckFinder(requests, auth)

        csv_opts = '-vsq' if cmd.verbose else '-sq'
        node_opts = '-v' if cmd.verbose else ''


        # ------------------------------------------------------------------------------------------------------------
        # run...

        checks = check_finder.find(None, None, None, ConfigurationCheckRequest.MODE.FULL)
        check_reports = {check.tag: check.rec for check in checks.items}

        if cmd.separate or cmd.latest:
            response = configuration_finder.find(None, False, cmd.request_mode())
            configs = [ConfigurationReport.construct(item, check_reports[item.tag]) for item in sorted(response.items)]

        if cmd.separate:
            for node in node_names:
                path = node + '.csv'
                logger.info("-")
                logger.info(path)

                generate_csv(configs, [node], path)

        if cmd.latest:
            logger.info(cmd.latest)
            generate_csv(configs, cmd.nodes, cmd.latest)

        if cmd.histories:
            Filesystem.mkdir(cmd.histories)
            tag_response = configuration_finder.find(None, False, ConfigurationRequest.MODE.TAGS_ONLY)

            for tag in sorted(tag_response.items):
                response = configuration_finder.find(tag, True, cmd.request_mode())
                configs = sorted(response.items)

                path = os.path.join(cmd.histories, tag + '-configs.csv')
                logger.info("-")
                logger.info(path)

                generate_csv(configs, cmd.nodes, path)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        now = LocalizedDatetime.now().utc().as_iso8601()
        logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
        exit(1)
