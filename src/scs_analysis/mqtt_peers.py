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
mqtt_peers.py { -i [-e] | -l [-n HOSTNAME] [-t TOPIC] | -s HOSTNAME TAG SHARED_SECRET TOPIC | -d HOSTNAME } [-v]

EXAMPLES
mqtt_peers.py -s scs-bbe-002 scs-be2-2 secret1 \
south-coast-science-dev/production-test/device/alpha-bb-eng-000002/status

csv_reader.py -v mqtt_peers.json | mqtt_peers.py -vie

FILES
~/SCS/aws/mqtt_peers.json

DOCUMENT EXAMPLE
{"peers": {"scs-bbe-002": {"hostname": "scs-bbe-002", "tag": "scs-be2-2", "shared-secret": "T9o7CMvDEemnaqB4",
"topic": "south-coast-science-dev/production-test/device/alpha-bb-eng-000002/control"}}

SEE ALSO
scs_analysis/aws_mqtt_control
scs_analysis/osio_mqtt_control
scs_mfr/aws_project
scs_mfr/shared_secret
scs_mfr/system_id
"""

import json
import sys

from scs_analysis.cmd.cmd_mqtt_peers import CmdMQTTPeers

from scs_core.data.json import JSONify

from scs_core.estate.mqtt_peer import MQTTPeer, MQTTPeerSet

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMQTTPeers()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("mqtt_peers: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # APIAuth...
    group = MQTTPeerSet.load(Host)


    # ----------------------------------------------------------------------------------------------------------------
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
                print("mqtt_peers: invalid document: %s" % jstr, file=sys.stderr)
                exit(1)

            group.insert(peer)

            if cmd.echo:
                print(jstr)
                sys.stdout.flush()

        group.save(Host)

        if cmd.verbose:
            print("mqtt_peers: inserted: %d" % document_count, file=sys.stderr)

        exit(0)

    # list...
    if cmd.list:
        if group is not None:
            subset = group.subset(hostname_substring=cmd.for_hostname, topic_substring=cmd.for_topic)
            document_count = len(subset)

            for peer in subset:
                print(JSONify.dumps(peer))
                sys.stdout.flush()

        if cmd.verbose:
            print("mqtt_peers: found: %d" % document_count, file=sys.stderr)

        exit(0)

    # set...
    if cmd.is_set_peer():
        peer = MQTTPeer(cmd.set_hostname, cmd.set_tag, cmd.set_shared_secret, cmd.set_topic)
        group.insert(peer)
        group.save(Host)

        print(JSONify.dumps(peer))

        exit(0)

    # delete...
    if cmd.is_delete_peer():
        deleted = group.remove(cmd.delete_hostname)
        document_count = 1 if deleted else 0

        group.save(Host)

        if cmd.verbose:
            print("mqtt_peers: deleted: %d" % document_count, file=sys.stderr)

        exit(0)
