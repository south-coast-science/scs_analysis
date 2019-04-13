#!/usr/bin/env python3

"""
Created on 12 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

examples:
{"msg": null, "err": {"code": "UNKNOWN_CMD", "value": "hello"}}
{"msg": {"op": "scs-rpi-006", "spec": "scs-rpi-006"}, "err": null}

deliver-change
870725f3-e692-4538-aa81-bfa8b51d44e7

south-coast-science-dev
43308b72-ad41-4555-b075-b4245c1971db

WARNING: fails on [Payload too big for realtime feed] message
"""

import sys

from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.manager.message_event_subscriber import MessageEventSubscriber

from scs_host.client.http_streaming_client import HTTPStreamingClient
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

topic = "/users/southcoastscience-dev/test/gases"
print(topic)

print("-")


# --------------------------------------------------------------------------------------------------------------------

def listener(event):
    print("listener: %s" % event)
    print("-")


# --------------------------------------------------------------------------------------------------------------------

subscriber = None

try:
    streaming_client = HTTPStreamingClient()
    auth = APIAuth.load(Host)

    subscriber = MessageEventSubscriber(streaming_client)
    subscriber.subscribe(listener, auth, topic)


# ----------------------------------------------------------------------------------------------------------------
# end...

except KeyboardInterrupt:
    print("osio_http_streaming_test: KeyboardInterrupt", file=sys.stderr)


except Exception as ex:
    raise


# ----------------------------------------------------------------------------------------------------------------
# close...

finally:
    if subscriber:
        subscriber.close()
