#!/usr/bin/env python3

"""
Created on 9 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The mqtt_control_auth utility is used to maintain a database of authentication documents for use with the
scs_analysis/aws_mqtt_control and scs_analysis/osio_mqtt_control utilities.

Authentication details for specific devices are available on request from South Coast Science, or can be obtained
using the appropriate scs_mfr command-line utilities.

SYNOPSIS
mqtt_control_auth.py { -l | [-s HOSTNAME TAG SHARED_SECRET TOPIC] [-d HOSTNAME] } [-v]

EXAMPLES
mqtt_control_auth.py -s scs-bbe-002 scs-be2-2 secret1 \
south-coast-science-dev/production-test/device/alpha-bb-eng-000002/status

FILES
~/SCS/aws/mqtt_control_auths.json

DOCUMENT EXAMPLE
{"auths": {"scs-rpi-006": {"hostname": "scs-rpi-006", "tag": "scs-ap1-6", "shared-secret": "secret2",
"topic": "south-coast-science-dev/development/auth/alpha-pi-eng-000006/control"}}}

SEE ALSO
scs_analysis/aws_mqtt_control
scs_analysis/osio_mqtt_control
scs_mfr/shared_secret
scs_mfr/system_id
scs_mfr/aws_project
"""

import sys

from scs_analysis.cmd.cmd_mqtt_control_auth import CmdMQTTControlAuth

from scs_core.data.json import JSONify

from scs_core.estate.mqtt_control_auth import MQTTControlAuth, MQTTControlAuthSet

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMQTTControlAuth()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("mqtt_control_auth: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # APIAuth...
    group = MQTTControlAuthSet.load(Host)

    if cmd.verbose and group is not None:
        print("mqtt_control_auth: %s" % group, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    # list...
    if cmd.list:
        if group is not None:
            for auth in group.auths:
                print(JSONify.dumps(auth))

        exit(0)

    # set...
    if cmd.is_set_auth():
        auth = MQTTControlAuth(cmd.auth_hostname, cmd.auth_tag, cmd.auth_shared_secret, cmd.auth_topic)
        group.insert(auth)
        group.save(Host)

    # delete...
    if cmd.is_delete_auth():
        group.remove(cmd.delete_hostname)
        group.save(Host)

    # report...
    if group:
        print(JSONify.dumps(group))
