#!/usr/bin/env python3

"""
Created on 4 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.aqcsv.connector.source_mapping import SourceMapping
from scs_core.data.json import JSONify


# --------------------------------------------------------------------------------------------------------------------

print("list...")
for mapping in SourceMapping.instances():
    print(mapping)
print("-")

print("find...")
topic = "particulates"
species = "pm2p5"
source = "N2"

pk = (topic, species, source)

mapping = SourceMapping.instance(pk)
print("pk:%s mapping:%s" % (pk, mapping))
print("-")

jstr = JSONify.dumps(mapping)
print(jstr)
print("-")

print("find...")
topic = "particulates"
species = "pm1"
source = "N3"

pk = (topic, species, source)

mapping = SourceMapping.instance(pk)
print("pk:%s mapping:%s" % (pk, mapping))
print("-")

jstr = JSONify.dumps(mapping)
print(jstr)
print("-")
