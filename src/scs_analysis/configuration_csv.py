#!/usr/bin/env python3

"""
Created on 7 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_monitor utility is used to download configuration information from all devices accessible to the
user, and render this in CSV form. Two modes are available:

* --latest - download the latest configuration for all devices, and save this in the named CSV file.

* --histories - download the history of configuration changes for all devices. Where there has been at least one
change in the configuration for each device, save the history files in the named directory.

SYNOPSIS
configuration_csv.py { -l LATEST_CSV | -d HISTORY_CSV_DIR } [-v]

EXAMPLES
configuration_csv.py -vl configs.csv

SEE ALSO
scs_analysis/configuration_auth
scs_analysis/configuration_monitor
scs_analysis/configuration_monitor_check

scs_mfr/configuration
"""

import os
import requests
import sys

from subprocess import Popen, PIPE

from scs_analysis.cmd.cmd_configuration_csv import CmdConfigurationCSV

from scs_core.aws.client.configuration_auth import ConfigurationAuth
from scs_core.aws.manager.configuration_finder import ConfigurationFinder, ConfigurationRequest

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

from scs_core.sys.filesystem import Filesystem
from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

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

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not ConfigurationAuth.exists(Host):
            logger.error('access key not available')
            exit(1)

        try:
            auth = ConfigurationAuth.load(Host, encryption_key=ConfigurationAuth.password_from_user())
        except (KeyError, ValueError):
            logger.error('incorrect password')
            exit(1)

        finder = ConfigurationFinder(requests, auth)

        csv_args = '-vs' if cmd.verbose else '-s'


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.latest:
            response = finder.find(None, False, ConfigurationRequest.MODE.LATEST)
            configs = sorted(response.items)

            jstr = '\n'.join([JSONify.dumps(config) for config in configs])
            path = cmd.latest

            p = Popen(['csv_writer.py', csv_args, path], stdin=PIPE)
            p.communicate(input=jstr.encode())

        if cmd.histories:
            Filesystem.mkdir(cmd.histories)
            tag_response = finder.find(None, False, ConfigurationRequest.MODE.TAGS_ONLY)

            for tag in sorted(tag_response.items):
                response = finder.find(tag, True, ConfigurationRequest.MODE.DIFF)
                configs = sorted(response.items)

                if len(configs) < 2:                # ignore single-row histories
                    continue

                jstr = '\n'.join([JSONify.dumps(config) for config in configs])
                path = os.path.join(cmd.histories, tag + '-configs.csv')

                p = Popen(['csv_writer.py', csv_args, path], stdin=PIPE)
                p.communicate(input=jstr.encode())


    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        now = LocalizedDatetime.now().utc().as_iso8601()
        logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
        exit(1)
