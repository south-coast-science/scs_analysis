#!/usr/bin/env python3

"""
Created on 7 Oct 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.manager.byline_manager import BylineManager

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

api_auth = APIAuth.load(Host)
print(api_auth)

manager = BylineManager(api_auth)
print(manager)
print("-")

# TopicBylineGroup...
group = manager.find_bylines_for_topic('')
print(group)
print("-")

print("latest pub: %s" % group.latest_pub())
print("latest rec: %s" % group.latest_rec())
print("-")

print(group.devices)
print("-")

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
print("-")

print("latest pub: %s" % group.latest_pub())
print("latest rec: %s" % group.latest_rec())
print("-")

print(group.device)
print("-")
