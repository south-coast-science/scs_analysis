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

SYNOPSIS
aws_mqtt_control.py { -p HOSTNAME | -d TAG SHARED_SECRET TOPIC } { -i | -r [CMD] } [-t TIMEOUT] [-v]

EXAMPLES
aws_mqtt_control.py -p scs-bbe-002 -r "disk_usage"

FILES
~/SCS/aws/aws_client_auth.json

SEE ALSO
scs_analysis/aws_client_auth
scs_analysis/aws_mqtt_client
scs_analysis/mqtt_peer
scs_mfr/aws_project
scs_mfr/shared_secret
scs_mfr/system_id
"""

import sys
import time

from AWSIoTPythonSDK.exception.operationError import operationError
from AWSIoTPythonSDK.exception.operationTimeoutException import operationTimeoutException

from scs_analysis.cmd.cmd_mqtt_control import CmdMQTTControl
from scs_analysis.handler.aws_mqtt_control_handler import AWSMQTTControlHandler

from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient, MQTTSubscriber

from scs_core.control.control_datum import ControlDatum

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.publication import Publication

from scs_core.estate.mqtt_peer import MQTTPeerSet

from scs_host.comms.stdio import StdIO

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    client = None
    pub_comms = None


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMQTTControl()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("aws_mqtt_control: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if cmd.is_stored_peer():
            peer_group = MQTTPeerSet.load(Host)
            peer = peer_group.peer(cmd.peer_hostname)

            if peer is None:
                print("aws_mqtt_control: no MQTT peer found for host '%s'." % cmd.peer_hostname,
                      file=sys.stderr)
                exit(2)

            if cmd.verbose:
                print("aws_mqtt_control: %s" % peer, file=sys.stderr)

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
            print("aws_mqtt_control: ClientAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("aws_mqtt_control: %s" % auth, file=sys.stderr)

        # responder...
        handler = AWSMQTTControlHandler()
        subscriber = MQTTSubscriber(topic, handler.handle)

        # client...
        client = MQTTClient(subscriber)

        if cmd.verbose:
            print("aws_mqtt_control: %s" % client, file=sys.stderr)
            sys.stderr.flush()

        # tag...
        host_tag = Host.name()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        client.connect(auth, False)

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
            now = LocalizedDatetime.now().utc()
            datum = ControlDatum.construct(host_tag, device_tag, now, cmd_tokens, key)

            publication = Publication(topic, datum)

            handler.set(publication)

            if cmd.verbose:
                print(datum, file=sys.stderr)
                sys.stderr.flush()

            # publish...
            try:
                success = client.publish(publication)

                if cmd.verbose:
                    print("paho: %s" % "1" if success else "0", file=sys.stderr)

            except (OSError, operationError, operationTimeoutException) as ex:
                print(ex.__class__.__name__, file=sys.stderr)

            # subscribe...
            timeout = time.time() + cmd.timeout

            if cmd.receipt or cmd.interactive:
                while True:
                    if handler.receipt:
                        if not handler.receipt.is_valid(key):
                            raise ValueError("invalid digest: %s" % handler.receipt)

                        if cmd.verbose:
                            print(handler.receipt, file=sys.stderr)

                        if handler.receipt.command.stderr:
                            print(*handler.receipt.command.stderr, sep='\n', file=sys.stderr)

                        if handler.receipt.command.stdout:
                            print(*handler.receipt.command.stdout, sep='\n')

                        break

                    if time.time() > timeout:           # was cmd.interactive and ...
                        break

                    time.sleep(0.1)

            if not cmd.interactive:
                break


        # ------------------------------------------------------------------------------------------------------------
        # end...

    except KeyboardInterrupt:
        if cmd.interactive:
            print("", file=sys.stderr)

        if cmd.verbose:
            print("aws_mqtt_control: KeyboardInterrupt", file=sys.stderr)

    finally:
        if client:
            client.disconnect()
