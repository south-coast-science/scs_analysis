#!/usr/bin/env python3

"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_monitor_check utility is used to report on the configuration monitor's attempt to access all of
the devices known to the system. Status levels are:

* NOR - NO RESPONSE
* ERR - ERROR
* M - MALFORMED:
* MSA - MALFORMED:SAMPLE
* MCO - MALFORMED:CONFIG
* NSP - NOT SUPPORTED
* R - RECEIVED:
* RNW - RECEIVED:NEW
* RUN - RECEIVED:UNCHANGED
* RUP - RECEIVED:UPDATED

SYNOPSIS
configuration_monitor_check.py { -c TAG | [-t TAG [-e]] [-r RESULT] [-o] } [-i INDENT] [-v]

EXAMPLES
configuration_monitor_check.py -r ERR | node.py -s | csv_writer.py

DOCUMENT EXAMPLE
{"tag": "scs-ph1-26", "rec": "2021-05-18T14:36:00Z", "result": "ERROR",
"context": ["TimeoutExpired(['./configuration'], 30)"]}

SEE ALSO
scs_analysis/configuration_csv
scs_analysis/configuration_monitor
scs_analysis/monitor_auth

scs_mfr/configuration
"""

import requests
import sys

from scs_analysis.cmd.cmd_configuration_monitor_check import CmdConfigurationMonitorCheck

from scs_core.aws.client.monitor_auth import MonitorAuth
from scs_core.aws.manager.configuration_check_finder import ConfigurationCheckFinder
from scs_core.aws.manager.configuration_check_requester import ConfigurationCheckRequester

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

        if not MonitorAuth.exists(Host):
            logger.error('MonitorAuth not available.')
            exit(1)

        try:
            auth = MonitorAuth.load(Host, encryption_key=MonitorAuth.password_from_user())
        except (KeyError, ValueError):
            logger.error('incorrect password.')
            exit(1)

        finder = ConfigurationCheckFinder(requests, auth)
        requester = ConfigurationCheckRequester(requests, auth)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.check_tag:
            response = requester.request(cmd.check_tag)
            print(response.result, file=sys.stderr)
            exit(0 if response.result == 'OK' else 1)

        response = finder.find(cmd.tag_filter, cmd.exact_match, cmd.result_code, cmd.response_mode())
        print(JSONify.dumps(sorted(response.items), indent=cmd.indent))
        logger.info('retrieved: %s' % len(response.items))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        now = LocalizedDatetime.now().utc().as_iso8601()
        logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
        exit(1)
