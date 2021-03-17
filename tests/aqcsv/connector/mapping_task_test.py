#!/usr/bin/env python3

"""
Created on 13 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json

from scs_core.aqcsv.connector.airnow_mapping_task import MappingTask

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify


# --------------------------------------------------------------------------------------------------------------------

org = "south-coast-science-demo"
group = "brighton"
loc = 1
topic = "particulates"
device = "praxis-000401"
parameters = ("val.pm1", "val.pm2p5", "val.pm10")
duration = 1
checkpoint = "**:/01:00"

agency_code = "AAAAAAAAAA"
site_code = "123MM123456789"
pocs = {"88101": 2, "85101": 3}

upload_start = LocalizedDatetime.construct_from_jdict("2019-03-13T12:45:00Z")
upload_end = LocalizedDatetime.construct_from_jdict("2019-03-14T12:45:00Z")

task = MappingTask(org, group, loc, topic, device, parameters, duration, checkpoint,
                   agency_code, site_code, pocs, upload_start, upload_end)
print(task)
print("-")

for mapping in task.mappings():
    print(mapping)
print("-")

print(task.environment_path())
print(task.status_path())
print("-")

jstr = JSONify.dumps(task)
print(jstr)
print("-")

remade = MappingTask.construct_from_jdict(json.loads(jstr))
print(task)
print("-")

equality = remade == task

print("remade == task: %s" % equality)
print("-")
