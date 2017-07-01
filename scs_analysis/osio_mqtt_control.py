#!/usr/bin/env python3

"""
Created on 9 May 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Use this script as a stand-alone controller, when osio_mqtt_client is not running.

Requires APIAuth and ClientAuth documents.

command line examples:
./osio_mqtt_control.py -r -d scs-ap1-6 00000000cda1f8b9 \
-t /orgs/south-coast-science-dev/development/device/alpha-pi-eng-000006/control shutdown now

./osio_mqtt_control.py -d scs-be2-3 5016BBBK202F \
-t /orgs/south-coast-science-dev/development/device/alpha-bb-eng-000003/control -r -v hello
"""

import random
import sys
import time

from scs_analysis.cmd.cmd_osio_mqtt_control import CmdOSIOMQTTControl

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
from scs_host.client.mqtt_client import MQTTClient
from scs_host.client.mqtt_client import MQTTSubscriber

from scs_host.comms.stdio import StdIO
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# subscription handler...

class OSIOMQTTControlHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__outgoing_pub = None
        self.__receipt = None


    # ----------------------------------------------------------------------------------------------------------------

    def set(self, outgoing_pub):
        self.__outgoing_pub = outgoing_pub
        self.__receipt = None


    def handle(self, pub):
        try:
            receipt = ControlReceipt.construct_from_jdict(pub.payload)
        except TypeError:
            return

        if receipt.tag == self.__outgoing_pub.payload.attn and receipt.omd == self.__outgoing_pub.payload.digest:
            self.__receipt = receipt


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def receipt(self):
        return self.__receipt


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "OSIOMQTTControlHandler:{outgoing_pub:%s, receipt:%s}" %  (self.__outgoing_pub, self.receipt)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    client = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOMQTTControl()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)


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
            sys.stderr.flush()

        # manager...
        manager = TopicManager(HTTPClient(), api_auth.api_key)

        # check topic...
        if not manager.find(cmd.topic):
            print("Topic not available: %s" % cmd.topic, file=sys.stderr)
            exit()

        # responder...
        handler = OSIOMQTTControlHandler()

        # client...
        subscriber = MQTTSubscriber(cmd.topic, handler.handle)

        client = MQTTClient(subscriber)
        client.connect(ClientAuth.MQTT_HOST, client_auth.client_id, client_auth.user_id, client_auth.client_password)

        # tag...
        tag = Host.name()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        while True:
            # cmd...
            if cmd.interactive:
                line = StdIO.prompt('> ')
                cmd_tokens = line.split() if len(line) > 0 else None

            else:
                cmd_tokens = cmd.cmd_tokens

            # datum...
            now = LocalizedDatetime.now()
            datum = ControlDatum.construct(tag, cmd.device_tag, now, cmd_tokens, cmd.device_host_id)

            publication = Publication(cmd.topic, datum)

            handler.set(publication)

            if cmd.verbose:
                print(datum, file=sys.stderr)
                sys.stderr.flush()

            # publish...
            while True:
                try:
                    success = client.publish(publication, ClientAuth.MQTT_TIMEOUT)

                    if not success:
                        print("abandoned", file=sys.stderr)
                        sys.stderr.flush()

                    break

                except Exception as ex:
                    print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
                    sys.stderr.flush()

                time.sleep(random.uniform(1.0, 2.0))

            # subscribe...
            timeout = time.time() + 15

            if cmd.receipt or cmd.interactive:
                while True:
                    if handler.receipt:
                        if not handler.receipt.is_valid(cmd.device_host_id):
                            raise ValueError("invalid digest: %s" % handler.receipt)

                        if cmd.verbose:
                            print(handler.receipt, file=sys.stderr)

                        if handler.receipt.command.stderr:
                            print(*handler.receipt.command.stderr, sep='\n', file=sys.stderr)

                        if handler.receipt.command.stdout:
                            print(*handler.receipt.command.stdout, sep='\n')

                        break

                    if cmd.interactive and time.time() > timeout:
                        break

                    time.sleep(0.1)

            if not cmd.interactive:
                break


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("osio_mqtt_control: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if client:
            client.disconnect()
