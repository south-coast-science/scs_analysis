#!/usr/bin/env python3

"""
Created on 20 Mar 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_median utility provides a median filter - the filter maintains an odd-numbered window on the input
data sequence, and outputs the middle item in the sorted list of items. The user can specify the
size of the window.

Input data is typically in the form of a JSON document. A command parameter specifies the path to the node within
the document that is to be filtered. The node is typically a leaf node integer or float. The output of the
sample_median utility includes the source value, and the smoothed value.

SYNOPSIS
sample_median.py [-w SIZE] [-p PRECISION] [-v] [PATH]

EXAMPLES
aws_topic_history.py -m60 /orgs/south-coast-science-demo/brighton/loc/1/gases | \
sample_median.py -w 3 -p 1 val.CO.cnc

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-bgx-401", "rec": "2018-03-27T09:54:41.042+00:00", "val": {
"NO2": {"weV": 0.29563, "aeV": 0.280879, "weC": 0.009569, "cnc": 61.0},
"Ox": {"weV": 0.406819, "aeV": 0.387443, "weC": -0.010706, "cnc": 34.7},
"NO": {"weV": 0.319692, "aeV": 0.292129, "weC": 0.028952, "cnc": 165.5},
"CO": {"weV": 0.395819, "aeV": 0.289317, "weC": 0.113108, "cnc": 311.3},
"sht": {"hmd": 82.4, "tmp": 12.6}}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2018-03-27T12:11:21.028+00:00", "val": {"CO": {"cnc": {"src": 262.1, "med": 368.0}}}}

RESOURCES
Median filter
https://en.wikipedia.org/wiki/Median_filter
"""

import sys

from scs_analysis.cmd.cmd_sample_median import CmdSampleMedian

from scs_core.data.json import JSONify
from scs_core.data.median_filter import MedianFilter
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleMedian()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_median: %s" % cmd, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    median_filter = MedianFilter(cmd.window)

    if cmd.verbose:
        print("sample_median: %s" % median_filter, file=sys.stderr)
        sys.stderr.flush()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            document_count += 1

            value = datum.node(cmd.path)

            if value is None:
                continue

            target = PathDict()

            if datum.has_path('rec'):
                target.copy(datum, 'rec')

            target.append(cmd.path + '.src', value)
            target.append(cmd.path + '.med', round(median_filter.compute(value), cmd.precision))

            print(JSONify.dumps(target.node()))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        print("sample_median: %s" % repr(ex), file=sys.stderr)
        exit(1)

    finally:
        if cmd.verbose:
            print("sample_median: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
