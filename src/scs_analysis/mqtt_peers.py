#!/usr/bin/env python3

"""
Created on 9 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The mqtt_peers utility is used to maintain a database of MQTT peers for use with the
scs_analysis/aws_mqtt_control and scs_analysis/osio_mqtt_control utilities.

Authentication details for specific devices are available on request from South Coast Science, or can be obtained
using the appropriate scs_mfr command-line utilities.

SYNOPSIS
mqtt_peers.py { -l [-f HOSTNAME] | [-s HOSTNAME TAG SHARED_SECRET TOPIC] [-d HOSTNAME] } [-v]

EXAMPLES
mqtt_peers.py -s scs-bbe-002 scs-be2-2 secret1 \
south-coast-science-dev/production-test/device/alpha-bb-eng-000002/status

FILES
~/SCS/aws/mqtt_peers.json

DOCUMENT EXAMPLE
{"peers": {"scs-rpi-006": {"hostname": "scs-rpi-006", "tag": "scs-ap1-6", "shared-secret": "secret2",
"topic": "south-coast-science-dev/development/peer/alpha-pi-eng-000006/control"}}}

SEE ALSO
scs_analysis/aws_mqtt_control
scs_analysis/osio_mqtt_control
scs_mfr/shared_secret
scs_mfr/system_id
scs_mfr/aws_project
"""

import sys

from scs_analysis.cmd.cmd_mqtt_peers import CmdMQTTPeers

from scs_core.data.json import JSONify

from scs_core.estate.mqtt_peer import MQTTPeer, MQTTPeerSet

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

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

    # list...
    if cmd.list:
        if group is not None:
            for peer in group.peers:
                print(JSONify.dumps(peer))

        exit(0)

    # find...
    if cmd.is_find_peer():
        for peer in group.subset(cmd.find_hostname):
            print(JSONify.dumps(peer))

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
        group.remove(cmd.delete_hostname)
        group.save(Host)

        exit(0)

    # report...
    if group:
        print(JSONify.dumps(group))
