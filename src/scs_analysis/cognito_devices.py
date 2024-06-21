#!/usr/bin/env python3

"""
Created on 24 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_devices utility is used to find, update or delete the Cognito identity records of SCS devices.

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
cognito_devices.py  [-c CREDENTIALS] { -F [{ -t DEVICE_TAG | -n INVOICE }] [-m] | -U DEVICE_TAG INVOICE |
-D DEVICE_TAG } [-i INDENT] [-v]

EXAMPLES
cognito_devices.py -vi4 -c super -F -m

DOCUMENT EXAMPLE
[
    {
        "username": "scs-ph1-8",
        "invoice": "INV-0000",
        "created": "2023-04-20T12:25:47Z",
        "last-updated": "2024-01-29T15:37:21Z"
    }
]

DOCUMENT EXAMPLE - WITH MEMBERSHIPS
[
    {
        "account": {
            "username": "scs-ph1-8",
            "invoice": "INV-0000",
            "created": "2023-04-20T12:25:47Z",
            "last-updated": "2024-01-29T15:37:21Z"
        },
        "memberships": [
            {
                "DeviceTag": "scs-ph1-8",
                "OrgID": 69,
                "DeploymentLabel": "SCS Dev / Mobile 8",
                "DevicePath": "south-coast-science-dev/mobile/device/praxis-handheld-000008/",
                "LocationPath": "south-coast-science-dev/mobile/loc/8/",
                "StartDatetime": "1970-01-01T00:00:00Z",
                "EndDatetime": null
            }
        ]
    }
]

SEE ALSO
scs_analysis/cognito_users
scs_analysis/cognito_user_credentials
scs_analysis/organisation_devices

RESOURCES
https://docs.aws.amazon.com/cognito/latest/developerguide/signing-up-users-in-your-app.html
https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-policies.html
"""

import sys

from scs_analysis.cmd.cmd_cognito_devices import CmdCognitoDevices

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_device import CognitoDeviceIdentity
from scs_core.aws.security.cognito_device_finder import CognitoDeviceFinder
from scs_core.aws.security.cognito_device_manager import CognitoDeviceManager
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_membership import CognitoMembership
from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.client.http_exception import HTTPException, HTTPConflictException

from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCognitoDevices()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('cognito_devices', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


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
        # resources...

        device_manager = CognitoDeviceManager()
        org_manager = OrganisationManager()
        finder = CognitoDeviceFinder()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            if cmd.tag is None:
                report = sorted(finder.find_all(auth.id_token))

            else:
                report = sorted(finder.find_by_tag(auth.id_token, cmd.tag))

            if cmd.invoice_number is not None:
                report = [device for device in report if device.invoice_number == cmd.invoice_number]

            if cmd.memberships:
                org_devices = org_manager.find_devices(auth.id_token)
                report = CognitoMembership.merge(report, org_devices)

        if cmd.update:
            # find...
            device = finder.get_by_tag(auth.id_token, cmd.update_tag)

            if device is None:
                logger.error("no device found for tag: '%s'." % cmd.update)
                exit(1)

            # if not CognitoDeviceIdentity.is_valid_invoice_number(cmd.update_invoice):
            #     logger.error("'%s' is not a valid invoice number." % cmd.update_invoice)
            #     exit(2)

            # update...
            updated = CognitoDeviceIdentity(cmd.update_tag, invoice_number=cmd.update_invoice)
            report = device_manager.update(auth.id_token, updated)

        if cmd.delete:
            device_manager.delete(auth.id_token, cmd.delete)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.find:
            logger.info("found: %s" % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPConflictException as ex:
        logger.error("the tag '%s' is already in use." % report.tag)
        exit(1)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
