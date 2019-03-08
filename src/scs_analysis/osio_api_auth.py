#!/usr/bin/env python3

"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The osio_api_auth utility is used to store or read the API key required by the OpenSensors.io Community Edition
historic data retrieval system.

SYNOPSIS
osio_api_auth.py [-s ORG_ID API_KEY] [-v]

EXAMPLES
osio_api_auth.py -v -s south-coast-science-demo 099add97-6e89-4801-8d12-dd617797cd3b

FILES
~/SCS/osio/osio_api_auth.json

DOCUMENT EXAMPLE
{"org-id": "south-coast-science-demo", "api-key": "099add97-6e89-4801-8d12-dd617797cd3b"}

SEE ALSO
scs_analysis/osio_topic_history
scs_analysis/osio_mqtt_client
scs_analysis/osio_mqtt_control
"""

import sys

from scs_core.data.json import JSONify
from scs_core.osio.client.api_auth import APIAuth

from scs_host.sys.host import Host

from scs_analysis.cmd.cmd_osio_api_auth import CmdOSIOAPIAuth


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOAPIAuth()

    if cmd.verbose:
        print("osio_api_auth: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    if cmd.set():
        auth = APIAuth(cmd.org_id, cmd.api_key)

        auth.save(Host)

    else:
        # find self...
        auth = APIAuth.load(Host)

    print(JSONify.dumps(auth))
