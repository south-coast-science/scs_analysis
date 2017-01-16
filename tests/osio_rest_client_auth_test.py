#!/usr/bin/env python3

"""
Created on 17 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

examples:
{"msg": null, "err": {"code": "UNKNOWN_CMD", "value": "hello"}}
{"msg": {"op": "scs-rpi-006", "spec": "scs-rpi-006"}, "err": null}
"""

from scs_core.osio.client.api_auth import APIAuth

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

org_id = "south-coast-science-dev"
print(org_id)

api_key = "43308b72-ad41-4555-b075-b4245c1971db"
print(api_key)

print("-")

# --------------------------------------------------------------------------------------------------------------------

auth = APIAuth(org_id, api_key)
print(auth)
print("-")

auth.save(Host)

auth = APIAuth.load(Host)
print(auth)
print("-")
