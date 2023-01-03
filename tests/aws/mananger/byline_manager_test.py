#!/usr/bin/env python3

"""
Created on 7 Oct 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json
import requests

from scs_core.aws.data.byline import DeviceBylineGroup
from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.data.json import JSONify


# --------------------------------------------------------------------------------------------------------------------

manager = BylineManager(requests)
print(manager)
print("1-")

# TopicBylineGroup...
group = manager.find_bylines_for_topic('acsoft/holding-pool/device/praxis-000752/status', excluded='/control')
print(group)
print("2-")

print("latest pub: %s" % group.latest_pub())
print("latest rec: %s" % group.latest_rec())
print("3-")

print(group.devices)
print("4-")

for device in group.devices:
    print(device)

    device_bylines = group.bylines_for_device(device)
    for device_byline in device_bylines:
        print(device_byline)

    print("-")

print("=")

# DeviceBylineGroup...
group = manager.find_bylines_for_device('scs-bgx-431')
print(group)
print("5-")

group = manager.find_bylines_for_device('scs-bgx-431', excluded='/control')
print(group)
print("6-")

print("latest pub: %s" % group.latest_pub())
print("latest rec: %s" % group.latest_rec())
print("7-")

print(group.device)
print("=")

jstr = JSONify.dumps(group.as_json())
print(jstr)
print("8-")

group = DeviceBylineGroup.construct_from_jdict(json.loads(jstr))
print(group)
print("9-")

print("latest pub: %s" % group.latest_pub())
print("latest rec: %s" % group.latest_rec())
print("X-")


group = manager.find_bylines()
print(group)
jstr = JSONify.dumps(group.as_json(), indent=4)
print(jstr)

