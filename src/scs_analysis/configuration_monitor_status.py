#!/usr/bin/env python3

"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_monitor_status utility is used to

SYNOPSIS
configuration_monitor_status.py [-t TAG] [-r RESULT] [-o] [-i INDENT] [-v]

EXAMPLES

DOCUMENT EXAMPLE
{"tag": "scs-bgx-003", "rec": "2021-04-14T08:49:22Z, "result": "ERROR", "context": "stderr output"}

SEE ALSO
scs_analysis/configuration_auth
scs_analysis/configuration_monitor
"""

import sys

from scs_analysis.cmd.cmd_configuration_monitor_status import CmdConfigurationMonitorStatus

from scs_core.aws.client.configuration_auth import ConfigurationAuth

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    manager = None
    group = None

    document_count = 0

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdConfigurationMonitorStatus()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('configuration_monitor_status', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not ConfigurationAuth.exists(Host):
            logger.error('access key not available')
            exit(1)

        try:
            key = ConfigurationAuth.load(Host, encryption_key=ConfigurationAuth.password_from_user())
        except (KeyError, ValueError):
            logger.error('incorrect password')
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # TODO: code goes here

    except KeyboardInterrupt:
        print(file=sys.stderr)
