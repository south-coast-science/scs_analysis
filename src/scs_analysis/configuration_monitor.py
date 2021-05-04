#!/usr/bin/env python3

"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_monitor utility is used to

SYNOPSIS
configuration_monitor.py [-t TAG] [{ -o | -h }] [-i INDENT] [-v]

EXAMPLES

DOCUMENT EXAMPLE


SEE ALSO
scs_analysis/configuration_auth
scs_analysis/configuration_monitor_status
"""

import requests
import sys

from scs_analysis.cmd.cmd_configuration_monitor import CmdConfigurationMonitor

from scs_core.aws.client.configuration_auth import ConfigurationAuth
from scs_core.aws.manager.configuration_finder import ConfigurationFinder, ConfigurationRequest

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

        if not ConfigurationAuth.exists(Host):
            logger.error('access key not available')
            exit(1)

        try:
            pass
            # auth = ConfigurationAuth.load(Host, encryption_key=ConfigurationAuth.password_from_user())
        except (KeyError, ValueError):
            logger.error('incorrect password')
            exit(1)

        finder = ConfigurationFinder(requests, auth)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        response = finder.find(cmd.tag_filter, cmd.response_mode())
        if response is None:
            if cmd.response_mode() == ConfigurationRequest.MODE.HISTORY:
                logger.error("Could not retrieve history, please check tag is entered correctly ")
            else:
                logger.error("Something went wrong ")

        else:
            print(JSONify.dumps(response.items, indent=cmd.indent))
            logger.info('retrieved: %s' % len(response.items))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        now = LocalizedDatetime.now().utc().as_iso8601()
        logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
