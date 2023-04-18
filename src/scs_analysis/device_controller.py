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
Usage: device_controller.py [-c CREDENTIALS] -t DEVICE_TAG [-m CMD_TOKENS] [-i INDENT] [-v]

EXAMPLES
device_controller.py -vi4 -c super -F -m

DOCUMENT EXAMPLE
{"username": "scs-ph1-28", "created": "2023-04-04T09:08:55Z", "last-updated": "2023-04-04T09:08:56Z"}

SEE ALSO
scs_analysis/cognito_credentials
scs_analysis/cognito_users
scs_analysis/organisation_devices

RESOURCES
https://docs.aws.amazon.com/cognito/latest/developerguide/signing-up-users-in-your-app.html
https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-policies.html
"""

import requests
import sys

from scs_analysis.cmd.cmd_device_controller import CmdDeviceController

from scs_core.aws.client.device_control_client import DeviceControlClient
from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPNotFoundException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    credentials = None
    auth = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdDeviceController()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('device_controller', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # auth...

        gatekeeper = CognitoLoginManager(requests)

        # CognitoUserCredentials...
        if not CognitoClientCredentials.exists(Host, name=cmd.credentials_name):
            logger.error("Cognito credentials not available.")
            exit(1)

        try:
            password = CognitoClientCredentials.password_from_user()
            credentials = CognitoClientCredentials.load(Host, name=cmd.credentials_name, encryption_key=password)
        except (KeyError, ValueError):
            logger.error("incorrect password.")
            exit(1)

        auth = gatekeeper.user_login(credentials)

        if not auth.is_ok():
            logger.error("login: %s" % auth.authentication_status.description)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        client = DeviceControlClient(requests)

        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.message:
            recipt = client.interrogate(auth.id_token, cmd.device_tag, cmd.message)
            report = recipt if cmd.wrapper else recipt.command

            print(JSONify.dumps(report, indent=cmd.indent))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPNotFoundException:
        logger.error("device '%s' not found." % cmd.device_tag)
        exit(1)
