#!/usr/bin/env python3

"""
Created on 28 Jun 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The device_monitor utility is used to

SYNOPSIS


EXAMPLES


DOCUMENT EXAMPLE

SEE ALSO
scs_analysis/alert_status
scs_analysis/cognito_user_credentials
"""

import requests
import sys

from scs_analysis.cmd.cmd_device_monitor import CmdDeviceMonitor

from scs_core.aws.client.api_auth import APIAuth

from scs_core.aws.security.cognito_device import CognitoDeviceCredentials

from scs_core.aws.manager.device_monitor_specification_manager import DeviceMonitorSpecificationManager

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException, HTTPNotFoundException

from scs_core.data.datum import Datum
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

        cmd = CmdDeviceMonitor()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('device_monitor', verbose=cmd.verbose)        # level=logging.DEBUG
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

        # APIAuth (for BylineManager)...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            logger.error("APIAuth is not available")
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        if cmd.email is not None and not Datum.is_email_address(cmd.email):
            logger.error("The email address '%s' is not valid." % cmd.email)
            exit(2)

        if cmd.device_tag is not None and not CognitoDeviceCredentials.is_valid_tag(cmd.device_tag):
            logger.error("The device tag '%s' is not valid." % cmd.device_tag)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        manager = DeviceMonitorSpecificationManager(requests)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            report = manager.find(auth.id_token, email_address=cmd.email, device_tag=cmd.device_tag, exact=True)

            print("report: %s" % report)

        # ------------------------------------------------------------------------------------------------------------
        # end...

        # report...
        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.find:
            logger.info('retrieved: %s' % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)
