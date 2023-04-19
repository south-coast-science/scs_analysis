#!/usr/bin/env python3

"""
Created on 17 Apr 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The cognito_users utility is used to

SYNOPSIS
Usage: device_controller.py [-c CREDENTIALS] -t DEVICE_TAG [-m CMD_TOKENS] [-i INDENT] [-v]

EXAMPLES
device_controller.py -vi4 -c super -F -m

SEE ALSO
scs_analysis/cognito_credentials
scs_analysis/cognito_users
scs_analysis/organisation_devices
"""

import json
import os
import requests
import sys

from scs_analysis.cmd.cmd_device_controller import CmdDeviceController

from scs_core.aws.client.device_control_client import DeviceControlClient
from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.data.json import AbstractPersistentJSONable, JSONify

from scs_core.sys.http_exception import HTTPNotFoundException
from scs_core.sys.logging import Logging

from scs_host.comms.stdio import StdIO
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

def print_output(command):
    if command.stderr:
        print(*command.stderr, sep='\n', file=sys.stderr)
        sys.stderr.flush()

    if command.stdout:
        print(*command.stdout, sep='\n')
        sys.stdout.flush()


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    history_filename = os.path.join(Host.scs_path(), AbstractPersistentJSONable.aws_dir(), 'device_controller')


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
        # StdIO settings...

        if not cmd.message:
            response = client.interrogate(auth.id_token, cmd.device_tag, ['?'])

            if response.command.stderr:
                logger.error("%s device problem: %s." % (cmd.device_tag, response.command.stderr[0]))
                exit(1)

            commands = json.loads(response.command.stdout[0])
            vocabulary = [command + ' ' for command in commands]

            StdIO.set(vocabulary=vocabulary, history_filename=history_filename)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.message:
            response = client.interrogate(auth.id_token, cmd.device_tag, cmd.message.split())

            if cmd.std:
                print_output(response.command)

            else:
                report = response if cmd.wrapper else response.command
                print(JSONify.dumps(report, indent=cmd.indent))

            exit(response.command.return_code)

        else:
            while True:
                line = StdIO.prompt(cmd.device_tag)

                if not line:
                    continue

                auth = gatekeeper.user_login(credentials)

                response = client.interrogate(auth.id_token, cmd.device_tag, line.split())
                print_output(response.command)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPNotFoundException:
        logger.error("device '%s' not found." % cmd.device_tag)
        exit(1)
