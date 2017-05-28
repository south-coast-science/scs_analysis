#!/usr/bin/env python3

"""
Created on 9 May 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Use this script in conjunction with osio_mqtt_client.py

Requires APIAuth and ClientAuth documents.

command line example:
./osio_device_control.py -d scs-bgx-120 5016BBBK20AB \
-t /orgs/south-coast-science-dev/unep/device/praxis-000120/control \
-p osio_mqtt_pub.uds -s control.uds uptime -v
"""

import json
import sys

from collections import OrderedDict

from scs_analysis.cmd.cmd_osio_device_control import CmdOSIODeviceControl

from scs_core.control.control_datum import ControlDatum
from scs_core.control.control_receipt import ControlReceipt

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.publication import Publication

from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.osio.manager.topic_manager import TopicManager

from scs_core.sys.exception_report import ExceptionReport

from scs_host.client.http_client import HTTPClient

from scs_host.sys.host import Host
from scs_host.sys.uds import UDS


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    client = None
    sub_comms = None
    receipt = None


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIODeviceControl()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # datum...

    tag = Host.name()
    now = LocalizedDatetime.now()

    datum = ControlDatum.construct(tag, cmd.device_tag, now, cmd.cmd_tokens, cmd.device_host_id)
    publication = Publication(cmd.topic, datum)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # APIAuth...
        api_auth = APIAuth.load_from_host(Host)

        if api_auth is None:
            print("APIAuth not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(api_auth, file=sys.stderr)

        # ClientAuth...
        client_auth = ClientAuth.load_from_host(Host)

        if client_auth is None:
            print("ClientAuth not available.", file=sys.stderr)
            exit()

        if cmd.verbose:
            print(client_auth, file=sys.stderr)

        # manager...
        manager = TopicManager(HTTPClient(), api_auth.api_key)

        # comms...
        pub_comms = UDS(cmd.uds_pub_addr)
        sub_comms = UDS(cmd.uds_sub_addr) if cmd.uds_sub_addr else None

        if cmd.verbose:
            print("pub: %s" % pub_comms, file=sys.stderr)
            print("sub: %s" % sub_comms, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # check topic...
        if not manager.find(cmd.topic):
            print("Topic not available: %s" % cmd.topic, file=sys.stderr)
            exit()

        if cmd.verbose:
            print(datum, file=sys.stderr)
            sys.stderr.flush()

        # publish...
        try:
            pub_comms.connect()
            pub_comms.write(JSONify.dumps(publication))

        finally:
            pub_comms.close()

        # subscribe...
        if sub_comms:
            sub_comms.connect()

            for message in sub_comms.read():
                jdict = json.loads(message, object_pairs_hook=OrderedDict)
                publication = Publication.construct_from_jdict(jdict)

                if publication.topic != cmd.topic:
                    continue

                receipt = ControlReceipt.construct_from_jdict(publication.payload)

                # correct receipt?...
                if receipt.tag == datum.attn and receipt.omd == datum.digest:
                    break

            # validate...
            if not receipt.is_valid(cmd.device_host_id):
                raise ValueError("invalid digest: %s" % receipt)

            if cmd.verbose:
                print(receipt, file=sys.stderr)

            # report...
            if receipt.command.stderr:
                print(*receipt.command.stderr, sep='\n', file=sys.stderr)

            if receipt.command.stdout:
                print(*receipt.command.stdout, sep='\n')


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("osio_device_control: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if client:
            client.disconnect()

        if sub_comms:
            sub_comms.close()
