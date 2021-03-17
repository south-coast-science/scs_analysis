#!/usr/bin/env python3

"""
Created on 13 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json

from scs_core.aqcsv.connector.airnow_mapping_task import MappingTask, AirNowMappingTaskList

from scs_core.data.json import JSONify

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

jstr1 = '{"org": "south-coast-science-demo", "group": "brighton", "loc": 2, "topic": "particulates", ' \
        '"device": "praxis-000401", "parameters": ["val.pm1", "val.pm2p5", "val.pm10"], "checkpoint": "**:/01:00", ' \
        '"site-code": "123MM123456789", "pocs": {"88101": 2, "85101": 3}, "latest-rec": "2019-03-13T12:45:00Z"}'

jstr2 = '{"org": "south-coast-science-demo", "group": "brighton", "loc": 1, "topic": "particulates", ' \
        '"device": "praxis-000401", "parameters": ["val.pm1", "val.pm2p5", "val.pm10"], "checkpoint": "**:/01:00", ' \
        '"site-code": "123MM123456789", "pocs": {"88101": 2, "85101": 3}, "latest-rec": "2019-03-13T12:45:00Z"}'

jstr3 = '{"org": "ricardo", "group": "heathrow", "loc": 1, "topic": "particulates", ' \
        '"device": "praxis-000401", "parameters": ["val.pm1", "val.pm2p5", "val.pm10"], "checkpoint": "**:/01:00", ' \
        '"site-code": "123MM123456789", "pocs": {"88101": 2, "85101": 3}, "latest-rec": "2019-03-13T12:45:00Z"}'

# --------------------------------------------------------------------------------------------------------------------


task1 = MappingTask.construct_from_jdict(json.loads(jstr1))
print(task1)
print("-")

task2 = MappingTask.construct_from_jdict(json.loads(jstr2))
print(task2)
print("-")

task3 = MappingTask.construct_from_jdict(json.loads(jstr3))
print(task3)
print("-")


tasks = AirNowMappingTaskList({})
tasks.insert(task1)
print(tasks)

tasks.insert(task2)
print(tasks)

tasks.insert(task3)
print(tasks)
print("-")

jstr = JSONify.dumps(tasks)
print(jstr)
print("-")

tasks.save(Host)
tasks = AirNowMappingTaskList.load(Host)
print(tasks)
print("-")

remade = AirNowMappingTaskList.construct_from_jdict(json.loads(jstr))
print("-")
print("-")

print(tasks)
print("-")
