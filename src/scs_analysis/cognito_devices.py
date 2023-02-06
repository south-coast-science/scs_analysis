#!/usr/bin/env python3

"""
Created on 24 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_users utility is used to create, update and retrieve AWS Cognito identities. This utility can only be used
by organisation administrators and superusers.

If the --Create function is used, an email is sent to the new user. The verification link in the email must be
excercised in order for the account to gain a CONFIRMED status.

SYNOPSIS
cognito_devices.py  [-c CREDENTIALS] { -F [-t TAG] | -C TAG SHARED_SECRET | -U TAG SHARED_SECRET | -D TAG }
[-i INDENT] [-v]

EXAMPLES
cognito_users.py -Fe bruno.beloff@southcoastscience.com

DOCUMENT EXAMPLE
{"username": "8", "creation-date": "2021-11-24T12:51:12Z", "confirmation-status": "CONFIRMED", "enabled": true,
"email": "bruno.beloff@southcoastscience.com", "given-name": "Bruno", "family-name": "Beloff", "is-super": true}

SEE ALSO
scs_analysis/cognito_credentials

RESOURCES
https://docs.aws.amazon.com/cognito/latest/developerguide/signing-up-users-in-your-app.html
https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-policies.html
"""

import requests
import sys

from scs_analysis.cmd.cmd_cognito_devices import CmdCognitoDevices

from scs_core.aws.security.cognito_device_manager import CognitoDeviceCreator, CognitoDeviceEditor, CognitoDeviceDeleter

from scs_core.aws.security.cognito_device import CognitoDeviceIdentity
from scs_core.aws.security.cognito_device_finder import CognitoDeviceFinder
from scs_core.aws.security.cognito_login_manager import CognitoUserLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials

from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException, HTTPConflictException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    credentials = None
    auth = None
    finder = None
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
        # auth...

        gatekeeper = CognitoUserLoginManager(requests)

        # CognitoUserCredentials...
        if not CognitoUserCredentials.exists(Host, name=cmd.credentials_name):
            logger.error("Cognito credentials not available.")
            exit(1)

        try:
            password = CognitoUserCredentials.password_from_user()
            credentials = CognitoUserCredentials.load(Host, name=cmd.credentials_name, encryption_key=password)
        except (KeyError, ValueError):
            logger.error("incorrect password")
            exit(1)

        try:
            auth = gatekeeper.login(credentials)

        except HTTPException as ex:
            logger.error(ex.data)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not cmd.create:
            finder = CognitoDeviceFinder(requests)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            if cmd.tag is not None:
                report = sorted(finder.find_by_tag(auth.id_token, cmd.tag))

            else:
                report = sorted(finder.find_all(auth.id_token))

        if cmd.create:
            if not CognitoDeviceIdentity.is_valid_password(cmd.create[1]):
                logger.error("password must be at least 16 characters.")
                exit(2)

            # create...
            identity = CognitoDeviceIdentity(cmd.create[0], cmd.create[1], None)

            manager = CognitoDeviceCreator(requests, auth.id_token)
            report = manager.create(identity)

        if cmd.update:
            if not CognitoDeviceIdentity.is_valid_password(cmd.update[1]):
                logger.error("password must be at least 16 characters.")
                exit(2)

            # find...
            device = finder.find_by_tag(auth.id_token, cmd.update[0])

            if device is None:
                logger.error("no device found for tag: '%s'." % cmd.update)
                exit(1)

            # update...
            report = CognitoDeviceIdentity(cmd.update[0], cmd.update[1], device.creation_date)

            auth = gatekeeper.login(credentials)                          # renew credentials
            manager = CognitoDeviceEditor(requests, auth.id_token)
            manager.update(report)

        if cmd.delete:
            # TODO: delete device from organisations
            manager = CognitoDeviceDeleter(requests, auth.id_token)
            manager.delete(cmd.delete)


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
