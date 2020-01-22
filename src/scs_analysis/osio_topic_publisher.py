#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The osio_topic_publisher utility is used to prepare data for publication by the osio_mqtt_client script. The
osio_topic_publisher works by taking data from stdin, wrapping it in a JSON document whose only field has the name of
the given topic, and presenting the result on stdout.

Note that the osio_topic_publisher in scs_analysis necessarily works differently to the osio_topic_publisher in scs_dev.
This is because scs_dev version has access to a device project specification, and therefore can find the topic path
automatically. For the scs_analysis version, the full topic path should be given explicitly.

SYNOPSIS
osio_topic_publisher.py -t TOPIC [-o] [-v]

EXAMPLES
osio_topic_publisher.py -t /users/southcoastscience-dev/test/json

SEE ALSO
scs_analysis/osio_mqtt_client

RESOURCES
https://opensensorsio.helpscoutdocs.com/article/84-overriding-timestamp-information-in-message-payload
"""

import json
import sys

from collections import OrderedDict

from scs_analysis.cmd.cmd_osio_topic_publisher import CmdOSIOTopicPublisher

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication

from scs_core.osio.config.project import Project

from scs_core.sys.system_id import SystemID

from scs_host.sys.host import Host


# TODO: remove channel handling

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOTopicPublisher()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("osio_topic_publisher: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # topic...
        if cmd.channel:
            # SystemID...
            system_id = SystemID.load(Host)

            if system_id is None:
                print("osio_topic_publisher: SystemID not available.", file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print("osio_topic_publisher: %s" % system_id, file=sys.stderr)

            project = Project.load(Host)

            if project is None:
                print("osio_topic_publisher: Project not available.", file=sys.stderr)
                exit(1)

            topic = project.channel_path(cmd.channel, system_id)

        else:
            topic = cmd.topic

        # TODO: check if topic exists

        if cmd.verbose:
            print("osio_topic_publisher: %s" % topic, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            try:
                jdict = json.loads(line)
            except ValueError:
                continue

            if cmd.override:
                payload = OrderedDict({'__timestamp': jdict['rec']})
                payload.update(jdict)

            else:
                payload = jdict

            # time.sleep(1)

            publication = Publication(topic, payload)

            print(JSONify.dumps(publication))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("osio_topic_publisher: KeyboardInterrupt", file=sys.stderr)
