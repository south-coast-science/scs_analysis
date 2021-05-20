#!/usr/bin/env python3

"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_monitor_check utility is used to

* NOR - NO RESPONSE
* ERR - ERROR
* M - MALFORMED:
* MSA - MALFORMED:SAMPLE
* MCO - MALFORMED:CONFIG
* R - RECEIVED:
* RNS - RECEIVED:NOT SUPPORTED
* RNW - RECEIVED:NEW
* RUN - RECEIVED:UNCHANGED
* RUP - RECEIVED:UPDATED

SYNOPSIS
configuration_monitor_check.py [-t TAG] [-r RESULT] [-o] [-i INDENT] [-v]

EXAMPLES

DOCUMENT EXAMPLE
{"tag": "scs-bgx-003", "rec": "2021-04-14T08:49:22Z, "result": "ERROR", "context": "stderr output"}

SEE ALSO
scs_analysis/configuration_auth
scs_analysis/configuration_monitor
"""

import requests
import sys

from scs_analysis.cmd.cmd_configuration_monitor_check import CmdConfigurationMonitorCheck

from scs_core.aws.client.configuration_auth import ConfigurationAuth
from scs_core.aws.manager.configuration_check_finder import ConfigurationCheckFinder

from scs_core.data.json import JSONify
from scs_core.data.datetime import LocalizedDatetime

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

        cmd = CmdConfigurationMonitorCheck()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('configuration_monitor_check', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not ConfigurationAuth.exists(Host):
            logger.error('access key not available')
            exit(1)

        try:
            pass
            # key = ConfigurationAuth.load(Host, encryption_key=ConfigurationAuth.password_from_user())
        except (KeyError, ValueError):
            logger.error('incorrect password')
            exit(1)

        finder = ConfigurationCheckFinder(requests, auth)

        # ------------------------------------------------------------------------------------------------------------
        # run...

        response = finder.find(cmd.tag_filter, cmd.result_code, cmd.response_mode())

        print(JSONify.dumps(sorted(response.items), indent=cmd.indent))
        logger.info('retrieved: %s' % len(response.items))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        now = LocalizedDatetime.now().utc().as_iso8601()
        logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
