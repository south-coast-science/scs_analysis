#!/usr/bin/env python3

"""
Created on 25 Dec 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_byline utility is used to find the date / time of the most-recently published message for a given topic
or device. The user may specify a topic path (find all devices that have published to the given topic), or a device tag
(find all topics which the given device has published to), but not both.

Output is in the form of zero or more JSON documents, indicating the device, topic and localised date / time for each
latest sense event.

SYNOPSIS
aws_byline.py { -d DEVICE | -t TOPIC [-l] } [-v]

EXAMPLES
aws_byline.py -t south-coast-science-demo/brighton/loc/1/gases

DOCUMENT EXAMPLE - OUTPUT
{"device": "scs-be2-3", "topic": "south-coast-science-dev/development/loc/1/gases", "rec": "2018-12-25T20:31:04Z"}

SEE ALSO
scs_analysis/aws_topic_history
"""

import sys

from scs_analysis.cmd.cmd_aws_byline import CmdAWSByline

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSByline()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("aws_byline: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # APIAuth...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            print("aws_byline: APIAuth not available.", file=sys.stderr)
            exit(1)

        # BylineManager...
        manager = BylineManager(HTTPClient(False), api_auth)

        if cmd.verbose:
            print("aws_byline: %s" % manager, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        latest = None

        try:
            # get...
            if cmd.topic:
                bylines = manager.find_bylines_for_topic(cmd.topic)

            else:
                bylines = manager.find_bylines_for_device(cmd.device)

            # process...
            for byline in bylines:
                if cmd.latest:
                    if latest is None or latest.rec < byline.rec:
                        latest = byline

                else:
                    print(JSONify.dumps(byline))
                    sys.stdout.flush()

            if cmd.latest and latest is not None:
                print(JSONify.dumps(latest))

        except HTTPException as ex:
            print("aws_byline: %s" % ex, file=sys.stderr)
            exit(1)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_byline: KeyboardInterrupt", file=sys.stderr)
