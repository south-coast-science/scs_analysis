#!/usr/bin/env python3

"""
Created on 8 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The aws_mqtt_control utility is used to interact with a remote host, using the device's control topic.
A command / receipt message regime provides an interactive system over the messaging infrastructure.

For security reasons, the user must be in possession of the target device's unique tag and shared secret.

SYNOPSIS
aws_mqtt_control.py -d TAG SHARED_SECRET TOPIC { -i | -r CMD } [-t TIMEOUT] [-v]

EXAMPLES
aws_mqtt_control.py -d scs-be2-2 5016BBBK202E \
south-coast-science-dev/production-test/device/alpha-bb-eng-000002/control -i

FILES
~/SCS/aws/aws_client_auth.json

SEE ALSO
scs_analysis/aws_client_auth
scs_analysis/aws_mqtt_client
scs_mfr/shared_secret
"""

import json
import sys
import time

from collections import OrderedDict

from scs_analysis.cmd.cmd_mqtt_control import CmdMQTTControl

from scs_core.control.control_datum import ControlDatum
from scs_core.control.control_receipt import ControlReceipt

from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient, MQTTSubscriber

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.publication import Publication

from scs_host.comms.stdio import StdIO

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class AWSMQTTControlHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__outgoing_pub = None
        self.__receipt = None


    # ----------------------------------------------------------------------------------------------------------------

    def set(self, outgoing_pub):
        self.__outgoing_pub = outgoing_pub
        self.__receipt = None


    # noinspection PyUnusedLocal,PyShadowingNames
    def handle(self, client, userdata, message):
        payload = json.loads(message.payload.decode(), object_pairs_hook=OrderedDict)

        try:
            receipt = ControlReceipt.construct_from_jdict(payload)
        except TypeError:
            return

        if receipt.tag == self.__outgoing_pub.payload.attn and receipt.omd == self.__outgoing_pub.payload.digest:
            self.__receipt = receipt


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def receipt(self):
        return self.__receipt


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTControlHandler:{outgoing_pub:%s, receipt:%s}" %  (self.__outgoing_pub, self.receipt)


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

        # ClientAuth...
        auth = ClientAuth.load(Host)

        if auth is None:
            print("aws_mqtt_control: ClientAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("aws_mqtt_control: %s" % auth, file=sys.stderr)

        # responder...
        handler = AWSMQTTControlHandler()
        subscriber = MQTTSubscriber(cmd.topic, handler.handle)

        # client...
        client = MQTTClient(subscriber)

        if cmd.verbose:
            print("aws_mqtt_control: %s" % client, file=sys.stderr)
            sys.stderr.flush()

        # tag...
        tag = Host.name()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        client.connect(auth)

        while True:
            # cmd...
            if cmd.interactive:
                line = StdIO.prompt(cmd.device_tag + ' > ')
                cmd_tokens = line.split() if len(line) > 0 else None

            else:
                cmd_tokens = cmd.cmd_tokens

            # datum...
            now = LocalizedDatetime.now()
            datum = ControlDatum.construct(tag, cmd.device_tag, now, cmd_tokens, cmd.device_host_id)

            publication = Publication(cmd.topic, datum)

            handler.set(publication)

            if cmd.verbose:
                print(datum, file=sys.stderr)
                sys.stderr.flush()

            # publish...
            client.publish(publication)

            # subscribe...
            timeout = time.time() + cmd.timeout

            if cmd.receipt or cmd.interactive:
                while True:
                    if handler.receipt:
                        if not handler.receipt.is_valid(cmd.device_host_id):
                            raise ValueError("invalid digest: %s" % handler.receipt)

                        if cmd.verbose:
                            print(handler.receipt, file=sys.stderr)

                        if handler.receipt.command.stderr:
                            print(*handler.receipt.command.stderr, sep='\n', file=sys.stderr)

                        if handler.receipt.command.stdout:
                            print(*handler.receipt.command.stdout, sep='\n')

                        break

                    if cmd.interactive and time.time() > timeout:
                        break

                    time.sleep(0.1)

            if not cmd.interactive:
                break


        # ----------------------------------------------------------------------------------------------------------------
        # end...

    except KeyboardInterrupt:
        if cmd.interactive:
            print("", file=sys.stderr)

        if cmd.verbose:
            print("aws_mqtt_control: KeyboardInterrupt", file=sys.stderr)

    finally:
        if client:
            client.disconnect()
