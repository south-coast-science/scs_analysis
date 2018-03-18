#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The aws_topic_publisher utility is used to prepare data for publication by the aws_mqtt_client script. The
aws_topic_publisher works by taking data from stdin, wrapping it in a JSON document whose only field has the name of
the given topic, and presenting the result on stdout.

Note that the aws_topic_publisher in scs_analysis necessarily works differently to the aws_topic_publisher in scs_dev.
This is because scs_dev version has access to a device project specification, and therefore can find the topic path
automatically. For the scs_analysis version, the full topic path should be given explicitly.

EXAMPLES
./aws_topic_publisher.py -t /users/southcoastscience-dev/test/json

SEE ALSO
scs_analysis/aws_mqtt_client
"""

import json
import sys

from collections import OrderedDict

from scs_analysis.cmd.cmd_aws_topic_publisher import CmdAWSTopicPublisher

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication

from scs_core.aws.config.project import Project

from scs_core.sys.exception_report import ExceptionReport
from scs_core.sys.system_id import SystemID

from scs_host.sys.host import Host


# TODO: remove project references

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSTopicPublisher()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # topic...
        if cmd.channel:
            # SystemID...
            system_id = SystemID.load(Host)

            if system_id is None:
                print("aws_topic_publisher: SystemID not available.", file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print(system_id, file=sys.stderr)

            # Project...
            project = Project.load(Host)

            if project is None:
                print("aws_topic_publisher: Project not available.", file=sys.stderr)
                exit(1)

            topic = project.channel_path(cmd.channel, system_id)

        else:
            topic = cmd.topic

        if cmd.verbose:
            print("topic: %s" % topic, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            try:
                jdict = json.loads(line, object_pairs_hook=OrderedDict)
            except ValueError:
                continue

            payload = jdict

            publication = Publication(topic, payload)

            print(JSONify.dumps(publication))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_topic_publisher: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
