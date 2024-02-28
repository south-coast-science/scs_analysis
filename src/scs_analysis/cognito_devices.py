#!/usr/bin/env python3

"""
Created on 24 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_devices utility is used to create, update and retrieve AWS Cognito identities. This utility can only be used
by customer organisation administrators, SCS administrators and superusers.

If the --Create function is used, an email is sent to the new user. The verification link in the email must be
excercised using the cognito_email utility in order for the account to gain a CONFIRMED status.

SYNOPSIS
cognito_devices.py  [-c CREDENTIALS] { -F [{ -t TAG | -n INVOICE }] [-m] | -U TAG INVOICE | -D TAG } [-i INDENT] [-v]

EXAMPLES
cognito_devices.py -vi4 -c super -F -m

DOCUMENT EXAMPLE
{"username": "scs-bgx-401", "invoice": "INV-000123",
"created": "2023-06-23T10:32:52+01:00", "last-updated": "2023-06-23T10:32:52+01:00"}

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
            updated = CognitoDeviceIdentity(cmd.update_tag, None, cmd.update_invoice, None, None)
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
