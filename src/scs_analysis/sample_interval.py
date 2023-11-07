#!/usr/bin/env python3

"""
Created on 16 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_interval utility is used to discover the jitter present in a data stream.

Input data must in the form of a JSON document. A command parameter specifies the path to the node within
the document that is to be measured. The node must represent time as an ISO 8601 localised date / time. The output of
the sample_interval utility includes the date / time value, and the time difference from the preceding value
in seconds.

SYNOPSIS
sample_interval.py [-p PRECISION] [-v] [PATH]

EXAMPLES
aws_topic_history.py -m1 /orgs/south-coast-science-demo/brighton/loc/1/gases | sample_interval.py -p3 rec

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-bgx-401", "rec": "2018-03-27T09:54:41.042+00:00", "val": {
"NO2": {"weV": 0.29563, "aeV": 0.280879, "weC": 0.009569, "cnc": 61.0},
"Ox": {"weV": 0.406819, "aeV": 0.387443, "weC": -0.010706, "cnc": 34.7},
"NO": {"weV": 0.319692, "aeV": 0.292129, "weC": 0.028952, "cnc": 165.5},
"CO": {"weV": 0.395819, "aeV": 0.289317, "weC": 0.113108, "cnc": 311.3},
"sht": {"hmd": 82.4, "tmp": 12.6}}}

DOCUMENT EXAMPLE - OUTPUT
{"time": "2018-03-27T10:14:51.028+00:00", "diff": 9.987}
"""

import sys

from scs_analysis.cmd.cmd_sample_interval import CmdSampleInterval

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.interval import Interval
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleInterval()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_interval: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        prev_time = None

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                break

            document_count += 1

            time = LocalizedDatetime.construct_from_iso8601(datum.node(cmd.path))

            interval = Interval.construct(prev_time, time, cmd.precision)
            print(JSONify.dumps(interval))
            sys.stdout.flush()

            prev_time = time

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        print("sample_interval: %s" % repr(ex), file=sys.stderr)
        exit(1)

    finally:
        if cmd.verbose:
            print("sample_interval: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
