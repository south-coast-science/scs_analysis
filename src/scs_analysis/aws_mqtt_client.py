#!/usr/bin/env python3

"""
Created on 4 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The aws_mqtt_client utility is used to subscribe or publish using the South Coast Science / AWS messaging
infrastructure.

Documents for publication are gained from stdin by default, otherwise from the specified Unix domain socket (UDS).
Likewise, documents gained from subscription are written to stdout, or a specified UDS.

Only one MQTT client should run at any one time, per TCP/IP host.

SYNOPSIS
aws_mqtt_client.py [-p UDS_PUB] [-s] [SUB_TOPIC_1 (UDS_SUB_1) .. SUB_TOPIC_N (UDS_SUB_N)] [-w] [-e] [-v]

EXAMPLES
aws_mqtt_client.py south-coast-science-dev/production-test/loc/1/gases

DOCUMENT EXAMPLE - OUTPUT
{"south-coast-science-demo/brighton/loc/1/climate":
{"tag": "scs-bgx-401", "rec": "2019-01-11T12:10:36Z", "val": {"hmd": 68.5, "tmp": 12.2}}}

{"tag": "scs-bgx-401", "rec": "2019-01-11T12:10:36Z", "val": {"hmd": 68.5, "tmp": 12.2}}

FILES
~/SCS/aws/aws_client_auth.json

SEE ALSO
scs_analysis/aws_client_auth
scs_analysis/aws_mqtt_control
scs_analysis/aws_topic_publisher

BUGS
When run as a background process, aws_mqtt_client will exit if it has no stdin stream.
"""

import json
import sys

from scs_analysis.cmd.cmd_mqtt_client import CmdMQTTClient
from scs_analysis.helper.aws_mqtt_client_handler import AWSMQTTClientHandler
from scs_analysis.helper.mqtt_reporter import MQTTReporter

from scs_core.aws.client.client_auth import ClientAuth
from scs_core.aws.client.mqtt_client import MQTTClient, MQTTSubscriber

from scs_core.data.publication import Publication

from scs_host.comms.domain_socket import DomainSocket
from scs_host.comms.stdio import StdIO

from scs_host.sys.host import Host


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
        print("aws_mqtt_client: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # ClientAuth...
        auth = ClientAuth.load(Host)

        if auth is None:
            print("aws_mqtt_client: ClientAuth not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("aws_mqtt_client: %s" % auth, file=sys.stderr)

        # comms...
        pub_comms = DomainSocket(cmd.uds_pub_addr) if cmd.uds_pub_addr else StdIO()

        # reporter...
        reporter = MQTTReporter(cmd.verbose)

        # subscribers...
        subscribers = []

        for subscription in cmd.subscriptions:
            sub_comms = DomainSocket(subscription.address) if subscription.address else StdIO()

            # handler...
            handler = AWSMQTTClientHandler(reporter, sub_comms, cmd.include_wrapper, cmd.echo)

            subscribers.append(MQTTSubscriber(subscription.topic, handler.handle))

        # client...
        client = MQTTClient(*subscribers)

        if cmd.verbose:
            print("aws_mqtt_client: %s" % client, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        client.connect(auth)

        pub_comms.connect()

        for message in pub_comms.read():
            try:
                jdict = json.loads(message)
            except ValueError:
                reporter.print("bad datum: %s" % message)
                continue

            publication = Publication.construct_from_jdict(jdict)

            success = client.publish(publication)

            reporter.print("done" if success else "abandoned")

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
