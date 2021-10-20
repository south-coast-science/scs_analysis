#!/usr/bin/env python3

"""
Created on 25 Dec 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_byline utility is used to find the date / time of the most-recently published message for a given topic
or device. The user may specify a topic path (find all devices that have published to the given topic), or a device tag
(find all topics which the given device has published to), but not both. A further option --all reports all bylines.

Output is in the form of zero or more JSON documents, indicating the device, topic and localised date / time for each
latest sense event.

SYNOPSIS
aws_byline.py { -d DEVICE | -t TOPIC [-l] | -a } [-x EXCLUDED] [-v]

EXAMPLES
aws_byline.py -t south-coast-science-demo -v -x /control

DOCUMENT EXAMPLE - OUTPUT
{"device": "scs-bgx-401", "topic": "south-coast-science-demo/brighton/loc/1/climate",
"lastSeenTime": "2020-10-23T08:52:20Z", "last_write": "2020-10-23T08:52:20Z",
"message": "{\"val\": {\"hmd\": 68.4, \"tmp\": 19.8, \"bar\": null}, \"rec\": \"2020-10-23T08:52:20Z\",
\"tag\": \"scs-bgx-401\"}"}

SEE ALSO
scs_analysis/aws_topic_history
"""

import sys

from scs_analysis.cmd.cmd_aws_byline import CmdAWSByline

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.client.network import Network
from scs_core.client.resource_unavailable_exception import ResourceUnavailableException

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
        manager = BylineManager(api_auth)

        if cmd.verbose:
            print("aws_byline: %s" % manager, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # check...

        if not Network.is_available():
            if cmd.verbose:
                print("aws_byline: waiting for network.", file=sys.stderr)
                sys.stderr.flush()

            Network.wait()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        latest = None

        # find...
        if cmd.topic:
            group = manager.find_bylines_for_topic(cmd.topic, excluded=cmd.excluded)

        elif cmd.device:
            group = manager.find_bylines_for_device(cmd.device, excluded=cmd.excluded)

        else:
            group = manager.find_bylines(excluded=cmd.excluded)     # all

        # report...
        for byline in group.bylines:
            if cmd.latest:
                if latest is None or latest.rec < byline.rec:
                    latest = byline

            else:
                jdict = byline.as_json(include_message=cmd.include_messages)
                print(JSONify.dumps(jdict))
                sys.stdout.flush()

        if cmd.latest and latest is not None:
            jdict = latest.as_json(include_message=cmd.include_messages)
            print(JSONify.dumps(jdict))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (ConnectionError, HTTPException) as ex:
        print("aws_byline: %s: %s" % (ex.__class__.__name__, ex), file=sys.stderr)

    except ResourceUnavailableException as ex:
        print("aws_byline: %s" % repr(ex), file=sys.stderr)

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        if cmd.verbose and group is not None and len(group):
            latest_pub = group.latest_pub()
            latest_iso = None if latest_pub is None else latest_pub.as_iso8601()

            print("aws_byline: latest_pub: %s" % latest_iso, file=sys.stderr)
