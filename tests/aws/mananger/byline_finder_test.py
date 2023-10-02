#!/usr/bin/env python3

"""
Created on 1 Aug 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json
import sys

from scs_core.aws.manager.byline.byline import DeviceBylineGroup
from scs_core.aws.manager.byline.byline_finder import BylineFinder

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.data.json import JSONify

from scs_host.sys.host import Host


# ------------------------------------------------------------------------------------------------------------
# authentication...

credentials = CognitoClientCredentials.load_for_user(Host, name='super')

if not credentials:
    exit(1)

gatekeeper = CognitoLoginManager()
auth = gatekeeper.user_login(credentials)

if not auth.is_ok():
    print("login: %s." % auth.authentication_status.description, file=sys.stderr)
    exit(1)


# --------------------------------------------------------------------------------------------------------------------

finder = BylineFinder()
print(finder)
print("1-")

# TopicBylineGroup...
group = finder.find_bylines_for_topic(auth.id_token, 'acsoft/holding-pool/device/praxis-000752/status',
                                      excluded='/control')
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
group = finder.find_bylines_for_device(auth.id_token, 'scs-opc-198')
print(group)
print("5-")

group = finder.find_bylines_for_device(auth.id_token, 'scs-opc-198', excluded='/control')
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


group = finder.find_bylines(auth.id_token)
print(group)
jstr = JSONify.dumps(group.as_json(), indent=4)
print(jstr)

