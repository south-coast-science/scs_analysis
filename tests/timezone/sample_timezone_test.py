#!/usr/bin/env python3

"""
Created on 19 Aug 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.sys.command import Command


# --------------------------------------------------------------------------------------------------------------------

timezone = 'Europe/London'

clu = Command(verbose=True)

p = clu.o(['csv_reader.py', '2021-autumn-utc.csv'])
p = clu.io(p, ['sample_timezone.py', timezone])
clu.i(p, ['csv_writer.py', '2021-autumn-london.csv'])

p = clu.o(['csv_reader.py', '2022-spring-utc.csv'])
p = clu.io(p, ['sample_timezone.py', timezone])
clu.i(p, ['csv_writer.py', '2022-spring-london.csv'])
