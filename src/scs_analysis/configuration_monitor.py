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
from scs_core.aws.manager.configuration_finder import ConfigurationFinder

from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None

    auth = None
    manager = None
    group = None

    document_count = 0

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
        print(JSONify.dumps(response.items, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error("HTTP response: %s (%s) %s" % (ex.status, ex.reason, ex.data))
