#!/usr/bin/env python3

"""
Created on 25 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_min utility is used to find the record with the lowest value for the given node.

Input data is typically in the form of a sequence of JSON documents. A command parameter specifies the path to the node
within the document that is to be tested. The node is typically a leaf node integer or float. The output of the
sample_min utility includes the whole input document.

SYNOPSIS
sample_min.py [-v] [PATH]

EXAMPLES
./osio_topic_history.py -m60 /orgs/south-coast-science-demo/brighton/loc/1/gases | ./sample_min.py val.CO.cnc

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-bgx-401", "rec": "2018-03-27T09:54:41.042+00:00", "val": {
"NO2": {"weV": 0.29563, "aeV": 0.280879, "weC": 0.009569, "cnc": 61.0},
"Ox": {"weV": 0.406819, "aeV": 0.387443, "weC": -0.010706, "cnc": 34.7},
"NO": {"weV": 0.319692, "aeV": 0.292129, "weC": 0.028952, "cnc": 165.5},
"CO": {"weV": 0.395819, "aeV": 0.289317, "weC": 0.113108, "cnc": 311.3},
"sht": {"hmd": 82.4, "tmp": 12.6}}}

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-bgx-401", "rec": "2018-03-27T09:54:41.042+00:00", "val": {
"NO2": {"weV": 0.29563, "aeV": 0.280879, "weC": 0.009569, "cnc": 61.0},
"Ox": {"weV": 0.406819, "aeV": 0.387443, "weC": -0.010706, "cnc": 34.7},
"NO": {"weV": 0.319692, "aeV": 0.292129, "weC": 0.028952, "cnc": 165.5},
"CO": {"weV": 0.395819, "aeV": 0.289317, "weC": 0.113108, "cnc": 311.3},
"sht": {"hmd": 82.4, "tmp": 12.6}}}
"""

import sys

from scs_analysis.cmd.cmd_sample_record import CmdSampleRecord

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleRecord()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)
        sys.stderr.flush()


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        min_datum = None

        for line in sys.stdin:
            sample_datum = PathDict.construct_from_jstr(line)

            if min_datum is None or sample_datum.node(cmd.path) < min_datum.node(cmd.path):
                min_datum = sample_datum

        if min_datum:
            print(JSONify.dumps(min_datum.node()))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_min: KeyboardInterrupt", file=sys.stderr)
