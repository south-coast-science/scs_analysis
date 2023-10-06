#!/usr/bin/env python3

"""
Created on 2 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_api_auth utility is used to store or read the endpoint host name, client ID and client certificate ID
required by the South Coast Science / AWS messaging infrastructure.

The certificate files - created using the AWS IoT tools - must be installed by hand.

SYNOPSIS
aws_client_auth.py [{ [-e ENDPOINT] [-c CLIENT_ID] [-I CERT_ID] | -d }] [-v]

EXAMPLES
aws_client_auth.py -e asrft7e5j5ecz.iot.us-west-2.amazonaws.com -c bruno -i 9f08402232

FILES
~/SCS/aws/aws_client_auth.json

~/SCS/aws/certs/XXX-certificate.pem.crt
~/SCS/aws/certs/XXX-private.pem.key
~/SCS/aws/certs/XXX-public.pem.key
~/SCS/aws/certs/root-CA.crt

DOCUMENT EXAMPLE
{"endpoint": "asrft7e5j5ecz.iot.us-west-2.amazonaws.com", "client-id": "bruno", "cert-id": "9f08402232"}

SEE ALSO
scs_analysis/aws_mqtt_client
scs_analysis/aws_mqtt_control
"""

import sys

from scs_core.aws.client.client_auth import ClientAuth
from scs_core.data.json import JSONify

from scs_host.sys.host import Host

from scs_analysis.cmd.cmd_aws_client_auth import CmdAWSClientAuth


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSClientAuth()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("aws_client_auth: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    auth = ClientAuth.load(Host)


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    if cmd.set():
        if auth is None and not cmd.is_complete():
            print("aws_client_auth: No configuration is stored - you must therefore set all fields.", file=sys.stderr)
            cmd.print_help(sys.stderr)
            exit(2)

        endpoint = cmd.endpoint if cmd.endpoint else auth.endpoint
        client_id = cmd.client_id if cmd.client_id else auth.client_id
        cert_id = cmd.cert_id if cmd.cert_id else auth.cert_id

        auth = ClientAuth(endpoint, client_id, cert_id)
        auth.save(Host)

    if cmd.delete:
        auth.delete(Host)
        auth = None

    if auth:
        print(JSONify.dumps(auth))
