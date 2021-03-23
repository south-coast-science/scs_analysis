#!/usr/bin/env python3

"""
Created on 9 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The mqtt_peers utility is used to maintain a database of MQTT peers for use with the
scs_analysis/aws_mqtt_control and scs_analysis/osio_mqtt_control utilities.

Options exist to find subsets of authentication documents according to hostname or control topic. Lists of
documents can be exported to or imported from CSV files, enabling the sharing of groups of documents between
users.

Authentication details for specific devices are available on request from South Coast Science, or can be obtained
using the appropriate scs_mfr command-line utilities.

SYNOPSIS
mqtt_peers.py { -p [-e] | -l [-n HOSTNAME] [-t TOPIC] | -m | -s HOSTNAME TAG SHARED_SECRET TOPIC | -d HOSTNAME } \
[-a] [-i INDENT] [-v]

EXAMPLES
mqtt_peers.py -s scs-bbe-002 scs-be2-2 secret1 \
south-coast-science-dev/production-test/device/alpha-bb-eng-000002/status

csv_reader.py -v mqtt_peers.json | mqtt_peers.py -vie

FILES
~/SCS/aws/mqtt_peers.json

DOCUMENT EXAMPLE
{"peers": {"scs-bbe-002": {"hostname": "scs-bbe-002", "tag": "scs-be2-2", "shared-secret": "T9o7CMvDB4",
"topic": "south-coast-science-dev/production-test/device/alpha-bb-eng-000002/control"}}

SEE ALSO
scs_dev/aws_mqtt_control

scs_mfr/aws_project
scs_mfr/shared_secret
scs_mfr/system_id
"""

import json
import sys

from scs_analysis.cmd.cmd_mqtt_peers import CmdMQTTPeers

from scs_core.aws.client.access_key import AccessKey
from scs_core.aws.client.client import Client
from scs_core.aws.manager.s3_manager import S3PersistenceManager, S3Manager

from scs_core.data.json import JSONify

from scs_core.estate.mqtt_device_poller import MQTTDevicePoller
from scs_core.estate.mqtt_peer import MQTTPeer, MQTTPeerSet

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    manager = None
    group = None

    key = None
    document_count = 0

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdMQTTPeers()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('mqtt_peers', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if cmd.aws or cmd.missing:
            if not AccessKey.exists(Host):
                logger.error('access key not available')
                exit(1)

            try:
                key = AccessKey.load(Host, encryption_key=AccessKey.password_from_user())
            except (KeyError, ValueError):
                logger.error('incorrect password')
                exit(1)

            client = Client.construct('s3', key)
            resource_client = Client.resource('s3', key)

            if cmd.aws:
                manager = S3PersistenceManager(client, resource_client)
            if cmd.missing:
                manager = S3Manager(client, resource_client)

        else:
            manager = Host

        if not cmd.missing:
            # MQTTPeerSet...
            group = MQTTPeerSet.load(manager)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # import...
        if cmd.is_import_peers():
            for line in sys.stdin:
                jstr = line.strip()

                if not jstr:
                    continue

                document_count += 1

                peer = MQTTPeer.construct_from_jdict(json.loads(jstr))

                if peer is None:
                    logger.error('invalid document: %s' % jstr)
                    exit(1)

                group.insert(peer)

                if cmd.echo:
                    print(jstr)
                    sys.stdout.flush()

            group.save(manager)
            logger.info('inserted: %d' % document_count)

        # list...
        if cmd.list:
            if group is not None:
                report = group.subset(hostname_substring=cmd.for_hostname, topic_substring=cmd.for_topic)

                print(JSONify.dumps(report, indent=cmd.indent))
                logger.info('found: %d' % len(report))

        # set...
        if cmd.is_set_peer():
            peer = MQTTPeer(cmd.set_hostname, cmd.set_tag, cmd.set_shared_secret, cmd.set_topic)
            group.insert(peer)
            group.save(manager)

            print(JSONify.dumps(peer, indent=cmd.indent))

        # delete...
        if cmd.is_delete_peer():
            deleted = group.remove(cmd.delete_hostname)
            document_count = 1 if deleted else 0

            group.save(manager)
            logger.info('deleted: %d' % document_count)

        # missing...
        if cmd.missing:
            reporter = MQTTDevicePoller(Host, manager)
            report = reporter.missing_devices()

            print(JSONify.dumps(report, indent=cmd.indent))
            logger.info('missing: %d' % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

