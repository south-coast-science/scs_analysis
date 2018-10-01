#!/usr/bin/env python3

"""
Created on 23 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The osio_mqtt_client utility is used to subscribe or publish using the OpenSensors.io Community Edition messaging
infrastructure.

OpenSensors.io API auth and client specifications must be installed on the host for the osio_mqtt_client
to operate. A specification should be obtained from the user's OpenSensors.io account.

Only one MQTT client should run at any one time, per TCP/IP host.

SYNOPSIS
osio_mqtt_client.py [-p UDS_PUB] [-s] [SUB_TOPIC_1 (UDS_SUB_1) .. SUB_TOPIC_N (UDS_SUB_N)] [-e] [-v]

EXAMPLES
./osio_mqtt_client.py /orgs/south-coast-science-dev/production-test/loc/1/gases

FILES
~/SCS/osio/osio_api_auth.json
~/SCS/osio/osio_client_auth.json

SEE ALSO
scs_analysis/osio_api_auth
scs_analysis/osio_mqtt_control
scs_analysis/osio_topic_publisher

BUGS
When run as a background process, osio_mqtt_client will exit if it has no stdin stream.
"""

import json
import random
import sys
import time

from collections import OrderedDict

from scs_philips_hue.cmd.cmd_mqtt_client import CmdMQTTClient
from scs_analysis.reporter.mqtt_reporter import MQTTReporter

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication

from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.osio.manager.topic_manager import TopicManager

from scs_core.sys.exception_report import ExceptionReport

from scs_host.client.http_client import HTTPClient
from scs_host.client.mqtt_client import MQTTClient, MQTTSubscriber

from scs_host.comms.domain_socket import DomainSocket
from scs_host.comms.stdio import StdIO

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class OSIOMQTTHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, mqtt_reporter, comms=None, echo=False):
        """
        Constructor
        """
        self.__reporter = mqtt_reporter
        self.__comms = comms
        self.__echo = echo


    # ----------------------------------------------------------------------------------------------------------------

    def handle(self, pub):
        try:
            self.__comms.connect()
            self.__comms.write(JSONify.dumps(pub), False)

        except ConnectionRefusedError:
            self.__reporter.print("connection refused for %s" % self.__comms.address)

        finally:
            self.__comms.close()

        if self.__echo:
            print(JSONify.dumps(pub))
            sys.stdout.flush()

        self.__reporter.print("received: %s" % JSONify.dumps(pub))


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "OSIOMQTTHandler:{reporter:%s, comms:%s, echo:%s}" % \
               (self.__reporter, self.__comms, self.__echo)


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
        print("osio_mqtt_client: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # APIAuth...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            print("osio_mqtt_client: APIAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("osio_mqtt_client: %s" % api_auth, file=sys.stderr)

        # ClientAuth...
        client_auth = ClientAuth.load(Host)

        if client_auth is None:
            print("osio_mqtt_client: ClientAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("osio_mqtt_client: %s" % client_auth, file=sys.stderr)

        # comms...
        pub_comms = DomainSocket(cmd.uds_pub_addr) if cmd.uds_pub_addr else StdIO()

        # manager...
        manager = TopicManager(HTTPClient(), api_auth.api_key)

        # check topics...
        unavailable = False
        for subscription in cmd.subscriptions:
            if not manager.find(subscription.topic):
                print("osio_mqtt_client: Topic not available: %s" % subscription[0], file=sys.stderr)
                unavailable = True

        if unavailable:
            exit(1)

        # reporter...
        reporter = MQTTReporter(cmd.verbose)

        # subscribers...
        subscribers = []

        for subscription in cmd.subscriptions:
            sub_comms = DomainSocket(subscription.address) if subscription.address else StdIO()

            # handler...
            handler = OSIOMQTTHandler(reporter, sub_comms, cmd.echo)

            if cmd.verbose:
                print("osio_mqtt_client: %s" % handler, file=sys.stderr)
                sys.stderr.flush()

            subscribers.append(MQTTSubscriber(subscription.topic, handler.handle))

        # client...
        client = MQTTClient(*subscribers)
        client.connect(ClientAuth.MQTT_HOST, client_auth.client_id, client_auth.user_id, client_auth.client_password)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # publish...
        pub_comms.connect()

        for message in pub_comms.read():
            try:
                datum = json.loads(message, object_pairs_hook=OrderedDict)
            except ValueError:
                reporter.print("bad datum: %s" % message)
                continue

            success = False

            while True:
                publication = Publication.construct_from_jdict(datum)

                try:
                    success = client.publish(publication, ClientAuth.MQTT_TIMEOUT)

                    if not success:
                        reporter.print("abandoned")

                    break

                except Exception as ex:
                    if cmd.verbose:
                        print(JSONify.dumps(ExceptionReport.construct(ex)))
                        sys.stderr.flush()

                time.sleep(random.uniform(1.0, 2.0))        # Don't hammer the broker!

            if success:
                reporter.print("done")

            if cmd.echo:
                print(message)
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("osio_mqtt_client: KeyboardInterrupt", file=sys.stderr)

    finally:
        if client:
            client.disconnect()

        if pub_comms:
            pub_comms.close()
