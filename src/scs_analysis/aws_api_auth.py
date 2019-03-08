#!/usr/bin/env python3

"""
Created on 2 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_api_auth utility is used to store or read the endpoint host name and API key required by the South Coast
Science / AWS historic data retrieval system.

SYNOPSIS
aws_api_auth.py [{ [-e ENDPOINT] [-a API_KEY] | -d }] [-v]

EXAMPLES
aws_api_auth.py -e aws.southcoastscience.com -a de92c5ff-b47a-4cc4-a04c-62d684d64a1f

FILES
~/SCS/aws/aws_api_auth.json

DOCUMENT EXAMPLE
{"endpoint": "aws.southcoastscience.com", "api-key": "de92c5ff-b47a-4cc4-a04c-62d684d64a1f"}

SEE ALSO
scs_analysis/aws_topic_history
"""

import sys

from scs_core.aws.client.api_auth import APIAuth
from scs_core.data.json import JSONify

from scs_host.sys.host import Host

from scs_analysis.cmd.cmd_aws_api_auth import CmdAWSAPIAuth


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSAPIAuth()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("aws_api_auth: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # APIAuth...
    auth = APIAuth.load(Host)


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    if cmd.set():
        if auth is None and not cmd.is_complete():
            print("aws_api_auth: No configuration is stored. You must therefore set all fields.", file=sys.stderr)
            cmd.print_help(sys.stderr)
            exit(1)

        endpoint = cmd.endpoint if cmd.endpoint else auth.endpoint
        api_key = cmd.api_key if cmd.api_key else auth.api_key

        auth = APIAuth(endpoint, api_key)
        auth.save(Host)

    if cmd.delete:
        auth.delete(Host)
        auth = None

    if auth:
        print(JSONify.dumps(auth))
