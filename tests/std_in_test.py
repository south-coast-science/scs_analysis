#!/usr/bin/env python3

'''
Created on 10 Sep 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
'''

import time

from scs_analysis.cmd.std_in import StdIn


# --------------------------------------------------------------------------------------------------------------------

conn = StdIn.construct()

while True:
    while not conn.poll():
        print("waiting")
        time.sleep(1)

    try:
        item = conn.recv()
    except EOFError:
        break

    # Process item
    print(item)         # Replace with useful work

# Shutdown
conn.close()

print("Consumer done")
