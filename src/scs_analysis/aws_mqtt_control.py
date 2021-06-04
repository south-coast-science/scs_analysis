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
"""

import json
import os
import sys
import time

from AWSIoTPythonSDK.exception.operationError import operationError
from AWSIoTPythonSDK.exception.operationTimeoutException import operationTimeoutException

from scs_analysis.cmd.cmd_mqtt_control import CmdMQTTControl

from scs_core.aws.client.access_key import AccessKey
from scs_core.aws.client.client import Client
from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient, MQTTSubscriber

from scs_core.aws.manager.s3_manager import S3PersistenceManager

from scs_core.control.control_datum import ControlDatum
from scs_core.control.control_handler import ControlHandler

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.publication import Publication

from scs_core.estate.mqtt_peer import MQTTPeerSet

from scs_core.sys.logging import Logging

from scs_host.comms.stdio import StdIO
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

EXIT_COMMANDS = ['reboot', 'shutdown']

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    history_filename = os.path.join(Host.scs_path(), AccessKey.aws_dir(), 'aws_mqtt_control_history')

    key = None
    client = None

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
                logger.error("access key not available")
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
        client = MQTTClient(subscriber)

        logger.info(client)


        # ------------------------------------------------------------------------------------------------------------
        # StdIO settings...

        client.connect(auth, False)

        if cmd.interactive:
            datum = ControlDatum.construct(host_tag, device_tag, LocalizedDatetime.now().utc(), '?',
                                           cmd.DEFAULT_TIMEOUT, key)
            publication = Publication(topic, datum)

            handler.set_outgoing(publication)

            try:
                client.publish(publication)
            except (OSError, operationError, operationTimeoutException) as ex:
                logger.error(ex.__class__.__name__)
                exit(1)

            timeout = time.time() + cmd.timeout

            while True:
                if handler.receipt:
                    if handler.receipt.command.stderr:
                        logger.error("%s device problem: %s." % (device_tag, handler.receipt.command.stderr[0]))
                        exit(1)

                    commands = json.loads(handler.receipt.command.stdout[0])
                    vocabulary = [command + ' ' for command in commands]

                    StdIO.set(vocabulary=vocabulary, history_filename=history_filename)
                    break

                if time.time() > timeout:
                    logger.error("%s is not available." % device_tag)
                    exit(1)

                time.sleep(0.1)


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

            # datum...
            datum = ControlDatum.construct(host_tag, device_tag, LocalizedDatetime.now().utc(), cmd_tokens,
                                           cmd.timeout, key)
            publication = Publication(topic, datum)

            handler.set_outgoing(publication)

            logger.info(datum)

            # publish...
            try:
                success = client.publish(publication)
                logger.info("paho: %s" % "1" if success else "0")

            except (OSError, operationError, operationTimeoutException) as ex:
                logger.error(ex.__class__.__name__)

            # subscribe...
            timeout = time.time() + cmd.timeout

            if cmd.receipt or cmd.interactive:
                while True:
                    if handler.receipt:
                        if not handler.receipt.is_valid(key):
                            raise ValueError("invalid digest: %s" % handler.receipt)

                        logger.info(handler.receipt)

                        if handler.receipt.command.stderr:
                            print(*handler.receipt.command.stderr, sep='\n')

                        if handler.receipt.command.stdout:
                            print(*handler.receipt.command.stdout, sep='\n')

                        break

                    if time.time() > timeout:
                        logger.error("timeout.")
                        break

                    time.sleep(0.1)

            if not cmd.interactive:
                break

            if cmd_tokens and cmd_tokens[0] in EXIT_COMMANDS:
                break


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)

    finally:
        StdIO.save_history(history_filename)

        if client:
            client.disconnect()
