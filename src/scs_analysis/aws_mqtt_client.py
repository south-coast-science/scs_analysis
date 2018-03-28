#!/usr/bin/env python3

"""
Created on 4 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The aws_mqtt_client utility is used to subscribe or publish using the South Coast Science / AWS messaging
infrastructure.

Note that AWS endpoint specification and client credentials must be installed on the host for the aws_mqtt_client
to operate.

Only one MQTT client should run at any one time, per TCP/IP host.

Note that there are currently no utilities to manage AWS configuration documents - these must be installed or edited
by hand. This situation will change.

EXAMPLES
./aws_mqtt_client.py south-coast-science-dev/production-test/loc/1/gases

FILES
~/SCS/aws/client_credentials.json
~/SCS/aws/endpoint.json

~/SCS/aws/certs/XXX-certificate.pem.crt
~/SCS/aws/certs/XXX-private.pem.key
~/SCS/aws/certs/XXX-public.pem.key
~/SCS/aws/certs/root-CA.crt

SEE ALSO
scs_analysis/aws_mqtt_control
scs_analysis/aws_topic_publisher

BUGS
When run as a background process, aws_mqtt_client will exit if it has no stdin stream.
"""

import json
import sys

from collections import OrderedDict

from scs_analysis.cmd.cmd_mqtt_client import CmdMQTTClient

from scs_core.aws.client.mqtt_client import MQTTClient, MQTTSubscriber
from scs_core.aws.client.client_credentials import ClientCredentials
from scs_core.aws.service.endpoint import Endpoint

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.publication import Publication

from scs_host.comms.domain_socket import DomainSocket
from scs_host.comms.stdio import StdIO

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class AWSMQTTHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, comms=None, echo=False, verbose=False):
        """
        Constructor
        """
        self.__comms = comms

        self.__echo = echo
        self.__verbose = verbose


    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyUnusedLocal,PyShadowingNames
    def handle(self, client, userdata, message):
        payload = json.loads(message.payload.decode(), object_pairs_hook=OrderedDict)

        pub = Publication(message.topic, payload)

        try:
            self.__comms.connect()
            self.__comms.write(JSONify.dumps(pub), False)

        except ConnectionRefusedError:
            if self.__verbose:
                print("AWSMQTTHandler: connection refused for %s" % self.__comms.address, file=sys.stderr)
                sys.stderr.flush()

        finally:
            self.__comms.close()

        if self.__echo:
            print(JSONify.dumps(pub))
            sys.stdout.flush()

        if self.__verbose:
            print("received: %s" % JSONify.dumps(pub), file=sys.stderr)
            sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTHandler:{comms:%s, echo:%s, verbose:%s}" % \
               (self.__comms, self.__echo, self.__verbose)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    client = None
    pub_comms = None


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMQTTClient()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # endpoint...
        endpoint = Endpoint.load(Host)

        if endpoint is None:
            print("aws_mqtt_client: Endpoint config not available.", file=sys.stderr)
            exit(1)

        # endpoint...
        credentials = ClientCredentials.load(Host)

        if credentials is None:
            print("aws_mqtt_client: ClientCredentials not available.", file=sys.stderr)
            exit(1)

        # comms...
        pub_comms = DomainSocket(cmd.uds_pub_addr) if cmd.uds_pub_addr else StdIO()

        # subscribers...
        subscribers = []

        for subscription in cmd.subscriptions:
            sub_comms = DomainSocket(subscription.address) if subscription.address else StdIO()

            # handler...
            handler = AWSMQTTHandler(sub_comms, cmd.echo, cmd.verbose)

            if cmd.verbose:
                print(handler, file=sys.stderr)

            subscribers.append(MQTTSubscriber(subscription.topic, handler.handle))

        # client...
        client = MQTTClient(*subscribers)

        if cmd.verbose:
            print(client, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        handler = AWSMQTTHandler()      # TODO: WTF?

        client.connect(endpoint, credentials)

        pub_comms.connect()

        for message in pub_comms.read():
            try:
                jdict = json.loads(message, object_pairs_hook=OrderedDict)
            except ValueError:
                continue

            publication = Publication.construct_from_jdict(jdict)

            client.publish(publication)

            if cmd.verbose:
                print("%s:         mqtt: done" % LocalizedDatetime.now().as_iso8601(), file=sys.stderr)
                sys.stderr.flush()

            if cmd.echo:
                print(message)
                sys.stdout.flush()


        # ----------------------------------------------------------------------------------------------------------------
        # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_mqtt_client: KeyboardInterrupt", file=sys.stderr)

    finally:
        if client:
            client.disconnect()

        if pub_comms:
            pub_comms.close()
