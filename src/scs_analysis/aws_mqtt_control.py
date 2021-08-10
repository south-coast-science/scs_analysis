#!/usr/bin/env python3

"""
Created on 8 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_mqtt_control utility is used to interact with a remote host, using the device's control topic.
A command / receipt message regime provides an interactive system over the messaging infrastructure.

For security reasons, the user must be in possession of the target device's unique tag and shared secret. These
tokens can be supplied on the command line, or sourced from an MQTT control auth document managed by the
mqtt_peer utility.

In order to publish on the MQTT control topic, the host must hold an appropriate authentication certificate.
Certificates are available on request from South Coast Science. The certificate should be indicated using the
aws_client_auth utility.

In the interactive mode, the aws_mqtt_control command-line interpreter supports history [UP] and [DOWN] keys.
The mode supports command completion with the [TAB] key and command listing with [TAB][TAB]. Exit from the interactive
mode with [CTRL-D].

SYNOPSIS
aws_mqtt_control.py { -p HOSTNAME [-a] | -d TAG SHARED_SECRET TOPIC } { -i | -r [CMD_TOKENS] } [-t TIMEOUT] [-v]

EXAMPLES
aws_mqtt_control.py -p scs-bbe-002 -r "disk_usage"

FILES
~/SCS/aws/aws_client_auth.json
~/SCS/aws/aws_mqtt_control_history

SEE ALSO
scs_analysis/aws_client_auth
scs_analysis/aws_mqtt_client
scs_analysis/mqtt_peer
scs_mfr/aws_project
scs_mfr/shared_secret
scs_mfr/system_id

BUGS
If the device is currently uploading a backlog of data, then the control receipt will be held in the device's
message queue, and the interaction will time out.
"""

import json
import os
import sys

from scs_analysis.cmd.cmd_mqtt_control import CmdMQTTControl

from scs_core.aws.client.access_key import AccessKey
from scs_core.aws.client.client import Client
from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient, MQTTSubscriber
from scs_core.aws.manager.s3_manager import S3PersistenceManager

from scs_core.control.control_handler import ControlHandler

from scs_core.estate.mqtt_peer import MQTTPeerSet

from scs_core.sys.logging import Logging

from scs_host.comms.stdio import StdIO
from scs_host.sys.host import Host


# TODO: when in non-interactive mode, exit return code should be the same as the command
# --------------------------------------------------------------------------------------------------------------------

EXIT_COMMANDS = ['reboot', 'restart', 'shutdown']

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    history_filename = os.path.join(Host.scs_path(), AccessKey.aws_dir(), 'aws_mqtt_control_history')

    key = None
    mqtt_client = None

    stdout = None
    stderr = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMQTTControl()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('aws_mqtt_control', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # tag...
        host_tag = Host.name()

        if cmd.aws:
            if not AccessKey.exists(Host):
                logger.error("AccessKey not available.")
                exit(1)

            try:
                key = AccessKey.load(Host, encryption_key=AccessKey.password_from_user())
            except (KeyError, ValueError):
                logger.error("incorrect password")
                exit(1)

            s3_client = Client.construct('s3', key)
            s3_resource_client = Client.resource('s3', key)

            manager = S3PersistenceManager(s3_client, s3_resource_client)

        else:
            manager = Host

        if cmd.is_stored_peer():
            peer_group = MQTTPeerSet.load(manager)
            peer = peer_group.peer(cmd.peer_hostname)

            if peer is None:
                logger.error("no MQTT peer found for host '%s'." % cmd.peer_hostname)
                exit(2)

            logger.info(peer)

            device_tag = peer.tag
            key = peer.shared_secret
            topic = peer.topic

        else:
            device_tag = cmd.device_tag
            key = cmd.device_shared_secret
            topic = cmd.device_topic

        # ClientAuth...
        auth = ClientAuth.load(Host)

        if auth is None:
            logger.error("ClientAuth not available.")
            exit(1)

        logger.info(auth)

        # responder...
        handler = ControlHandler(host_tag, device_tag)
        subscriber = MQTTSubscriber(topic, handler.handle)

        # client...
        mqtt_client = MQTTClient(subscriber)

        logger.info(mqtt_client)


        # ------------------------------------------------------------------------------------------------------------
        # StdIO settings...

        mqtt_client.connect(auth, False)

        if cmd.interactive:
            try:
                stdout, stderr = handler.publish(mqtt_client, topic, ['?'], cmd.DEFAULT_TIMEOUT, key)
            except TimeoutError:
                logger.error("%s is not available." % device_tag)
                exit(1)

            if stderr:
                logger.error("%s device problem: %s." % (device_tag, stderr[0]))
                exit(1)

            commands = json.loads(stdout[0])
            vocabulary = [command + ' ' for command in commands]

            StdIO.set(vocabulary=vocabulary, history_filename=history_filename)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        while True:
            # cmd...
            if cmd.interactive:
                line = StdIO.prompt(device_tag + ' > ')

                if not line:
                    continue

                cmd_tokens = line.split()

            else:
                cmd_tokens = cmd.cmd_tokens

            # publish...
            try:
                stdout, stderr = handler.publish(mqtt_client, topic, cmd_tokens, cmd.timeout, key)
            except TimeoutError:
                logger.error("%s is not available." % device_tag)
                exit(1)

            if stdout:
                print(*stdout, sep='\n')
                sys.stdout.flush()

            if stderr:
                print(*stderr, sep='\n', file=sys.stderr)
                sys.stderr.flush()

            if not cmd.interactive:
                break

            if cmd_tokens and cmd_tokens[0] in EXIT_COMMANDS:
                break


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (OSError, TimeoutError):
        logger.error("device is not available.")

    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)

    finally:
        StdIO.save_history(history_filename)

        if mqtt_client:
            mqtt_client.disconnect()
