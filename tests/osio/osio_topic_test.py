#!/usr/bin/env python3

"""
Created on 10 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

examples:
{"msg": null, "err": {"code": "UNKNOWN_CMD", "value": "hello"}}
{"msg": {"op": "scs-rpi-006", "spec": "scs-rpi-006"}, "err": null}

deliver-change
870725f3-e692-4538-aa81-bfa8b51d44e7

south-coast-science-dev
43308b72-ad41-4555-b075-b4245c1971db
"""

from scs_core.osio.manager.topic_manager import TopicManager


# --------------------------------------------------------------------------------------------------------------------

org_id = "south-coast-science-dev"
api_key = "43308b72-ad41-4555-b075-b4245c1971db"


# --------------------------------------------------------------------------------------------------------------------

# manager...
manager = TopicManager(api_key)
print(manager)
print("=")

topics = manager.find_for_org(org_id)

for topic in topics:
    print(topic)
    print("-")
