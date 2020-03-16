#!/usr/bin/env python3

"""
Created on 12 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

examples:
{"msg": null, "err": {"code": "UNKNOWN_CMD", "value": "hello"}}
{"msg": {"op": "scs-rpi-006", "spec": "scs-rpi-006"}, "err": null}

south-coast-science-dev
43308b72-ad41-4555-b075-b4245c1971db
"""

from scs_core.client.http_client import HTTPClient

from scs_core.data.datetime import LocalizedDatetime

from scs_core.osio.manager.message_manager import MessageManager


# --------------------------------------------------------------------------------------------------------------------

org_id = "south-coast-science-dev"
print(org_id)

api_key = "43308b72-ad41-4555-b075-b4245c1971db"
print(api_key)

topic = "/orgs/south-coast-science-dev/exhibition/loc/1/climate"
print(topic)

end_date = LocalizedDatetime.now().utc()
start_date = LocalizedDatetime.construct_from_timestamp(end_date.timestamp() - 60)

print("start: %s" % start_date)
print("end: %s" % end_date)

print("-")


# --------------------------------------------------------------------------------------------------------------------

# manager...
manager = MessageManager(HTTPClient(False), api_key)
print(manager)
print("=")


messages = manager.find_for_topic(topic, start_date, end_date)

print("got:%d" % (len(messages)))
print("-")

for message in messages:
    print(message)

print("-")
