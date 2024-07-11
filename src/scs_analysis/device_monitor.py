#!/usr/bin/env python3

"""
Created on 28 Jun 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The device monitor periodically checks on the availability and health of every air quality monitoring device.
The device_monitor utility is used to manage the email addresses for alerts associated with individual devices.

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
device_monitor.py [-c CREDENTIALS] { -F [{ -e EMAIL_ADDR | -t DEVICE_TAG } [-x]] | -A EMAIL_ADDR DEVICE_TAG [-j] |
-S DEVICE_TAG { 0 | 1 } | -D EMAIL_ADDR [{ -t DEVICE_TAG | -f }] } [-i INDENT] [-v]

EXAMPLES
device_monitor.py -c super -Ft scs-bgx-570

DOCUMENT EXAMPLE
{
    "scs-bgx-570": {
        "device-tag": "scs-bgx-570",
        "recipients": [
            {
                "email": "bruno.beloff@southcoastscience.com",
                "json-message": false
            }
        ],
        "suspended": false
    }
}

SEE ALSO
scs_analysis/cognito_user_credentials
scs_analysis/device_monitor_status
"""

import sys

from scs_analysis.cmd.cmd_device_monitor import CmdDeviceMonitor

from scs_core.aws.manager.byline.byline_finder import BylineFinder

from scs_core.aws.monitor.device.device_monitor_specification_manager import DeviceMonitorSpecificationManager

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException, HTTPNotFoundException

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.estate.device_tag import DeviceTag

from scs_core.email.email import EmailRecipient

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    response = None
    report = None

    # ------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdDeviceMonitor()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('device_monitor', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        credentials = CognitoClientCredentials.load_for_user(Host, name=cmd.credentials_name)

        if not credentials:
            exit(1)

        gatekeeper = CognitoLoginManager()
        auth = gatekeeper.user_login(credentials)

        if not auth.is_ok():
            logger.error("login: %s." % auth.authentication_status.description)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        if cmd.email is not None and cmd.exact_match and not Datum.is_email_address(cmd.email):
            logger.error("The email address '%s' is not valid." % cmd.email)
            exit(2)

        if cmd.device_tag is not None and cmd.exact_match and not DeviceTag.is_valid(cmd.device_tag):
            logger.error("The device tag '%s' is not valid." % cmd.device_tag)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        manager = DeviceMonitorSpecificationManager()
        byline_finder = BylineFinder()


        # ------------------------------------------------------------------------------------------------------------
        # identity...

        if cmd.device_tag:
            group = byline_finder.find_bylines_for_device(auth.id_token, cmd.device_tag)

            if not group:
                logger.error("device '%s' not found." % cmd.device_tag)
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            report = manager.find(auth.id_token, email_address=cmd.email, device_tag=cmd.device_tag,
                                  exact=cmd.exact_match)

        elif cmd.add:
            receipient = EmailRecipient(cmd.email, cmd.json_message)
            report = manager.add(auth.id_token, cmd.device_tag, receipient)

        elif cmd.suspend:
            report = manager.set_suspended(auth.id_token, cmd.device_tag, bool(cmd.is_suspended))

        elif cmd.delete:
            report = manager.remove(auth.id_token, cmd.email, device_tag=cmd.device_tag)


        # ------------------------------------------------------------------------------------------------------------
        # end...

        # report...
        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.find:
            logger.info('retrieved: %s' % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPNotFoundException:
        logger.error("device '%s' not found." % cmd.device_tag)
        exit(1)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
