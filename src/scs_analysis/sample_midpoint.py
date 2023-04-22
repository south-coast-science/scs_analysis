#!/usr/bin/env python3

"""
Created on 23 Aug 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_midpoint utility computes a linear regression for a stream of data delivered on stdin, it then finds the
midpoint y value. This is similar to an averaging function, but is independent of sampling jitter.

Input data is typically in the form of a JSON document. A command parameter specifies the path to the node within
the document that is to be averaged. The node is typically a leaf node integer or float. The output of the
sample_midpoint utility includes the source value, and the midpoint value.

SYNOPSIS
sample_midpoint.py [-t TALLY] [-p PRECISION] [-v] [PATH]

EXAMPLES
aws_topic_history.py -m60 /orgs/south-coast-science-demo/brighton/loc/1/gases | \
sample_midpoint.py -t360 -p1 val.CO.cnc

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-bgx-401", "rec": "2018-03-27T09:54:41.042+00:00", "val": {
"NO2": {"weV": 0.29563, "aeV": 0.280879, "weC": 0.009569, "cnc": 61.0},
"Ox": {"weV": 0.406819, "aeV": 0.387443, "weC": -0.010706, "cnc": 34.7},
"NO": {"weV": 0.319692, "aeV": 0.292129, "weC": 0.028952, "cnc": 165.5},
"CO": {"weV": 0.395819, "aeV": 0.289317, "weC": 0.113108, "cnc": 311.3},
"sht": {"hmd": 82.4, "tmp": 12.6}}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2018-03-27T16:14:01.033+00:00", "mid-rec": "2018-03-27T15:44:06.000+00:00",
"val": {"CO": {"cnc": {"src": 359.0, "mid": 296.5}}}}
"""


import sys

from scs_analysis.cmd.cmd_sample_tally import CmdSampleTally
from scs_analysis.handler.sample_midpoint import SampleMidpoint

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleTally()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_midpoint: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        sampler = SampleMidpoint(cmd.path, cmd.tally, cmd.precision)

        if cmd.verbose:
            print("sample_midpoint: %s" % sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            document_count += 1

            min_avg_max = sampler.datum(datum)

            if min_avg_max is not None:
                print(JSONify.dumps(min_avg_max))
                sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        print("sample_midpoint: %s" % repr(ex), file=sys.stderr)
        exit(1)

    finally:
        if cmd.verbose:
            print("sample_midpoint: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
