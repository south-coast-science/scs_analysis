#!/usr/bin/env python3

"""
Created on 17 Apr 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The device_controller utility is used to interact with a remote host, using the device's control topic.
A command / receipt message regime provides an interactive system over the messaging infrastructure.

An appropriate email address and password must have been stored using the cognito_credentials utility.

In the interactive mode, the aws_mqtt_control command-line interpreter supports history [UP] and [DOWN] keys.
The mode supports command completion with the [TAB] key and command listing with [TAB][TAB]. Exit from the interactive
mode with [CTRL-D].

A maximum of 30 seconds is available for the device to respond to the published message. After this time, the
device_controller utility will terminate.

SYNOPSIS
device_controller.py [-c CREDENTIALS] -t DEVICE_TAG [-m CMD_TOKENS [{ [-w] [-i INDENT] | -s }]] [-v]

EXAMPLES
device_controller.py -c super -t scs-be2-3 -m "vcal_baseline -i4" -s

SEE ALSO
scs_analysis/cognito_user_credentials

BUGS
On macOS, interactive history features require full disk access for the Terminal app:

PermissionError: [Errno 1] Operation not permitted after macOS Catalina Update
https://stackoverflow.com/questions/58479686/permissionerror-errno-1-operation-not-permitted-after-macos-catalina-update
"""

import json
import os
import sys

from scs_analysis.cmd.cmd_device_controller import CmdDeviceController

from scs_core.aws.client.device_control_client import DeviceControlClient
from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException, HTTPNotFoundException, HTTPGatewayTimeoutException, \
    HTTPServiceUnavailableException

from scs_core.data.json import AbstractPersistentJSONable, JSONify

from scs_core.sys.logging import Logging

from scs_host.comms.stdio import StdIO
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

EXIT_COMMANDS = ['reboot', 'restart', 'shutdown']


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

    history_filename = os.path.join(Host.scs_path(), AbstractPersistentJSONable.aws_dir(), 'device_controller.history')


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

        client = DeviceControlClient()


        # ------------------------------------------------------------------------------------------------------------
        # StdIO settings...

        if not cmd.message:
            response = client.interact(auth.id_token, cmd.device_tag, ['?'])

            if response.command.stderr:
                logger.error("%s device problem: %s." % (cmd.device_tag, response.command.stderr[0]))
                exit(1)

            commands = json.loads(response.command.stdout[0])
            vocabulary = [command + ' ' for command in commands]

            StdIO.set(vocabulary=vocabulary, history_filename=history_filename)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.message:
            response = client.interact(auth.id_token, cmd.device_tag, cmd.message.split())

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

                cmd_tokens = line.split()

                auth = gatekeeper.user_login(credentials)
                response = client.interact(auth.id_token, cmd.device_tag, cmd_tokens)
                print_output(response.command)

                if cmd_tokens and cmd_tokens[0] in EXIT_COMMANDS:
                    exit(0)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPNotFoundException:
        logger.error("device '%s' not found." % cmd.device_tag)
        exit(1)

    except HTTPGatewayTimeoutException:
        logger.error("device '%s' is not available." % cmd.device_tag)
        exit(1)

    except HTTPServiceUnavailableException:
        logger.error("device '%s' is interacting with another controller." % cmd.device_tag)
        exit(1)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    finally:
        StdIO.save_history(history_filename)
