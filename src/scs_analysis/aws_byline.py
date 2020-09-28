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
{"device": "scs-bgx-401", "topic": "south-coast-science-demo/brighton/loc/1/particulates",
"pub": "2020-09-25T11:49:46Z", "rec": "2020-09-25T11:49:40Z"}

SEE ALSO
scs_analysis/aws_topic_history
"""

import sys

from scs_analysis.cmd.cmd_aws_byline import CmdAWSByline

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.client.http_client import HTTPClient
from scs_core.client.network_unavailable_exception import NetworkUnavailableException

from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    group = None

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

        # get...
        if cmd.topic:
            group = manager.find_bylines_for_topic(cmd.topic)

        else:
            group = manager.find_bylines_for_device(cmd.device)

        # process...
        for byline in group.bylines:
            if cmd.latest:
                if latest is None or latest.rec < byline.rec:
                    latest = byline

            else:
                print(JSONify.dumps(byline))
                sys.stdout.flush()

        if cmd.latest and latest is not None:
            print(JSONify.dumps(latest))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (ConnectionError, HTTPException) as ex:
        print("aws_byline: %s: %s" % (ex.__class__.__name__, ex), file=sys.stderr)

    except NetworkUnavailableException:
        print("aws_byline: network not available.", file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("aws_byline: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose and group is not None and len(group):
            latest_pub = group.latest_pub()
            latest_iso = None if latest_pub is None else latest_pub.as_iso8601()

            print("aws_byline: latest_pub: %s" % latest_iso, file=sys.stderr)
