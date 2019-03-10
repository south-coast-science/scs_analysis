#!/usr/bin/env python3

"""
Created on 18 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_topic_publisher utility is used to prepare data for publication by the aws_mqtt_client script. The
aws_topic_publisher acts by taking data from stdin, wrapping it in a JSON document whose only field has the name of
the given topic, and presenting the result on stdout.

Note that the aws_topic_publisher in scs_analysis necessarily works differently to the aws_topic_publisher in scs_dev.
This is because scs_dev version has access to the device's project specification, and therefore can find the topic path
automatically. For the scs_analysis version, the full topic path should be given explicitly.

SYNOPSIS
aws_topic_publisher.py -t TOPIC [-v]

EXAMPLES
aws_topic_publisher.py -t /users/southcoastscience-dev/test/json

SEE ALSO
scs_analysis/aws_mqtt_client
"""

import json
import sys

from scs_analysis.cmd.cmd_aws_topic_publisher import CmdAWSTopicPublisher

from scs_core.data.json import JSONify
from scs_core.data.publication import Publication


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSTopicPublisher()

    if cmd.verbose:
        print("aws_topic_publisher: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            try:
                jdict = json.loads(line)
            except ValueError:
                continue

            publication = Publication(cmd.topic, jdict)

            print(JSONify.dumps(publication))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_topic_publisher: KeyboardInterrupt", file=sys.stderr)
