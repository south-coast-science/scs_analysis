#!/usr/bin/env python3

"""
Created on 7 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_monitor utility is used to download configuration information from all devices accessible to the
user, and render this in CSV form. Three modes are available:

* --latest - download the latest configuration for all devices, and save this in the named CSV file.

* --diff-histories - download the history of configuration changes for all devices. Where there has been at least one
change in the configuration for each device, save the history files in the named directory.

* --full-histories - download the history of all configuration changes for all devices.

Nodes fields may be any of:

hostname, packs, afe-baseline, afe-id, aws-api-auth, aws-client-auth, aws-group-config, aws-project, csv-logger-conf,
display-conf, gas-baseline, gas-model-conf, gps-conf, interface-conf, greengrass-identity, mpl115a2-calib, mqtt-conf,
ndir-conf, opc-conf, pmx-model-conf, pressure-conf, psu-conf, psu-version, pt1000-calib, scd30-baseline, scd30-conf,
schedule, shared-secret, sht-conf, sht-conf, networks, modem, sim, system-id, timezone-conf

If no nodes are specified, then the full configuration is reported.

SYNOPSIS
configuration_csv.py { -l LATEST_CSV | { -d | -f } HISTORIES_CSV_DIR } [-v] [NODE_1..NODE_N]

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
from scs_core.aws.manager.configuration_finder import ConfigurationFinder, ConfigurationRequest

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

from scs_core.sys.filesystem import Filesystem
from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    NODES = ('hostname', 'packs', 'afe-baseline', 'afe-id', 'aws-api-auth', 'aws-client-auth', 'aws-group-config',
             'aws-project', 'csv-logger-conf', 'display-conf', 'gas-baseline', 'gas-model-conf', 'gps-conf',
             'interface-conf', 'greengrass-identity', 'mpl115a2-calib', 'mqtt-conf', 'ndir-conf', 'opc-conf',
             'pmx-model-conf', 'pressure-conf', 'psu-conf', 'psu-version', 'pt1000-calib', 'scd30-baseline',
             'scd30-conf', 'schedule', 'shared-secret', 'sht-conf', 'sht-conf', 'networks', 'modem', 'sim',
             'system-id', 'timezone-conf')

    logger = None
    auth = None

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
            if node not in NODES:
                logger.error('nodes must be in: %s' % str(NODES))
                exit(2)

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not MonitorAuth.exists(Host):
            logger.error('MonitorAuth not available.')
            exit(1)

        try:
            auth = MonitorAuth.load(Host, encryption_key=MonitorAuth.password_from_user())
        except (KeyError, ValueError):
            logger.error('incorrect password.')
            exit(1)

        finder = ConfigurationFinder(requests, auth)

        csv_args = '-vs' if cmd.verbose else '-s'
        node_args = '-v' if cmd.verbose else ''

        nodes = ['tag', 'rec'] + ['val.' + node for node in cmd.nodes]


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.latest:
            response = finder.find(None, False, cmd.request_mode())
            configs = sorted(response.items)

            jstr = '\n'.join([JSONify.dumps(config) for config in configs])
            path = cmd.latest

            if cmd.nodes:
                p = Popen(['node.py', node_args] + nodes, stdin=PIPE, stdout=PIPE)
                csv_data, _ = p.communicate(input=jstr.encode())
            else:
                csv_data = jstr.encode()

            p = Popen(['csv_writer.py', csv_args, path], stdin=PIPE)
            p.communicate(input=csv_data)

        if cmd.histories:
            Filesystem.mkdir(cmd.histories)
            tag_response = finder.find(None, False, ConfigurationRequest.MODE.TAGS_ONLY)

            for tag in sorted(tag_response.items):
                response = finder.find(tag, True, cmd.request_mode())
                configs = sorted(response.items)

                if len(configs) < 2:                # ignore single-row histories
                    continue

                jstr = '\n'.join([JSONify.dumps(config) for config in configs])
                path = os.path.join(cmd.histories, tag + '-configs.csv')

                if cmd.nodes:
                    p = Popen(['node.py', node_args] + nodes, stdin=PIPE, stdout=PIPE)
                    csv_data, _ = p.communicate(input=jstr.encode())
                else:
                    csv_data = jstr.encode()

                p = Popen(['csv_writer.py', csv_args, path], stdin=PIPE)
                p.communicate(input=csv_data)


    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        now = LocalizedDatetime.now().utc().as_iso8601()
        logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
        exit(1)
