#!/usr/bin/env python3

"""
Created on 24 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_low_pass utility provides a rolling exponential average or low pass filter. The user must specify the
sampling interval in seconds, together with the cut-off frequency.

Input data is typically in the form of a JSON document. A command parameter specifies the path to the node within
the document that is to be filtered. The node is typically a leaf node integer or float. The output of the
sample_low_pass utility includes the source value, and the smoothed value.

SYNOPSIS
sample_low_pass.py -d DELTA_T -c CUT_OFF [-p PRECISION] [-v] [PATH]

EXAMPLES
osio_topic_history.py -m60 /orgs/south-coast-science-demo/brighton/loc/1/gases | \
sample_low_pass.py -d 10.0 -c 0.02 -p 1 val.CO.cnc

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-bgx-401", "rec": "2018-03-27T09:54:41.042+00:00", "val": {
"NO2": {"weV": 0.29563, "aeV": 0.280879, "weC": 0.009569, "cnc": 61.0},
"Ox": {"weV": 0.406819, "aeV": 0.387443, "weC": -0.010706, "cnc": 34.7},
"NO": {"weV": 0.319692, "aeV": 0.292129, "weC": 0.028952, "cnc": 165.5},
"CO": {"weV": 0.395819, "aeV": 0.289317, "weC": 0.113108, "cnc": 311.3},
"sht": {"hmd": 82.4, "tmp": 12.6}}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2018-03-27T10:55:11.033+00:00", "val": {"CO": {"cnc": {"src": 121.3, "lpf": 131.3}}}}

RESOURCES
Ten Little Algorithms, Part 2: The Single-Pole Low-Pass Filter
https://www.embeddedrelated.com/showarticle/779.php
"""

import sys

from scs_analysis.cmd.cmd_sample_low_pass import CmdLowPass

from scs_core.data.json import JSONify
from scs_core.data.low_pass_filter import LowPassFilter
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdLowPass()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_low_pass: %s" % cmd, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    lpf = LowPassFilter.construct(cmd.delta, cmd.cut_off)

    if cmd.verbose:
        print("sample_low_pass: %s" % lpf, file=sys.stderr)
        sys.stderr.flush()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                break

            document_count += 1

            value = datum.node(cmd.path)

            if value is None:
                break

            target = PathDict()

            if datum.has_path('rec'):
                target.copy(datum, 'rec')

            target.append(cmd.path + '.src', value)
            target.append(cmd.path + '.lpf', round(lpf.line(value), cmd.precision))

            print(JSONify.dumps(target.node()))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyError as ex:
        print("sample_low_pass: KeyError: %s" % ex, file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_low_pass: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_low_pass: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
