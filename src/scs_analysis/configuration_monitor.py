#!/usr/bin/env python3

"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_monitor utility is used to retrieve configuration information relating to one or more devices.
Flags enable the selection of either the latest recorded configuration for the device(s), or a history of
configuration changes. In the case of historical reports, either all the field values can be returned, or
only those that changed from the previous recording.

SYNOPSIS
configuration_monitor.py [-t TAG [-e]] { -l | -f | -d | -o } [-i INDENT] [-v]

EXAMPLES
configuration_monitor.py -t scs-bgx-401 -d | node.py -s | csv_writer.py -s

SEE ALSO
scs_analysis/configuration_csv
scs_analysis/configuration_monitor_check
scs_analysis/monitor_auth

scs_mfr/configuration
"""

import requests
import sys

from scs_analysis.cmd.cmd_configuration_monitor import CmdConfigurationMonitor

from scs_core.aws.client.monitor_auth import MonitorAuth
from scs_core.aws.manager.configuration_finder import ConfigurationFinder

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

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

        cmd = CmdConfigurationMonitor()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('configuration_monitor', verbose=cmd.verbose)
        logger = Logging.getLogger()

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


        # ------------------------------------------------------------------------------------------------------------
        # run...

        response = finder.find(cmd.tag_filter, cmd.exact_match, cmd.response_mode())

        print(JSONify.dumps(sorted(response.items), indent=cmd.indent))
        logger.info('retrieved: %s' % len(response.items))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        now = LocalizedDatetime.now().utc().as_iso8601()
        logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
        exit(1)
