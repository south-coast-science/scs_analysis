#!/usr/bin/env python3

"""
Created on 28 Jun 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The device monitor periodically checks on the availability and health of every air quality monitoring device. The
device_monitor_status utility is used to manage the email addresses associated with individual devices.

SYNOPSIS


EXAMPLES


DOCUMENT EXAMPLE

SEE ALSO
scs_analysis/alert_status
scs_analysis/cognito_user_credentials
"""

import requests
import sys

from scs_analysis.cmd.cmd_device_monitor_status import CmdDeviceMonitorStatus

from scs_core.aws.manager.device_monitor_status_manager import DeviceMonitorStatusManager

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_device import CognitoDeviceCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException

from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    response = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdDeviceMonitorStatus()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('device_monitor_status', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)

        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        credentials = CognitoClientCredentials.load_for_user(Host, name=cmd.credentials_name)

        if not credentials:
            exit(1)

        gatekeeper = CognitoLoginManager(requests)
        auth = gatekeeper.user_login(credentials)

        if not auth.is_ok():
            logger.error("login: %s" % auth.authentication_status.description)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        if cmd.tag_filter is not None and cmd.exact_match and not CognitoDeviceCredentials.is_valid_tag(cmd.tag_filter):
            logger.error("The device tag '%s' is not valid." % cmd.tag_filter)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        manager = DeviceMonitorStatusManager(requests)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        report = manager.find(auth.id_token, device_tag_filter=cmd.tag_filter, exact=cmd.exact_match)


        # ------------------------------------------------------------------------------------------------------------
        # end...

        # report...
        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))
            logger.info('retrieved: %s' % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)
