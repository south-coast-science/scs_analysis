#!/usr/bin/env python3

"""
Created on 23 Oct 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_slope utility it used to find the slope for a given field in a sequence of JSON documents. Slope is
defined as change in value / change in time (in seconds).

The output document replaced the input field with field.cur (the current value) and field.slope. For the initial
input document, the corresponding output document's field.slope value is null. A --tally flag specifies the number
of rolling samples in the regression.

SYNOPSIS
sample_slope.py [-i ISO] [-t TALLY] [-p PRECISION] [-v] PATH

EXAMPLES
csv_reader.py -v ~/climate.csv | sample_slope.py -v val.tmp

DOCUMENT EXAMPLE - INPUT
{"val": {"hmd": 67.6, "tmp": 20.5, "bar": ""}, "rec": "2020-10-23T12:19:20Z", "tag": "scs-bgx-401"}

DOCUMENT EXAMPLE - OUTPUT
{"val": {"hmd": 67.6, "tmp": {"cur": 20.5, "slope": -0.001667}, "bar": ""}, "rec": "2020-10-23T12:19:20Z",
"tag": "scs-bgx-401"}
"""

import sys

from scs_analysis.cmd.cmd_sample_slope import CmdSampleSlope

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.datum import Datum
from scs_core.data.json import JSONify
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleSlope()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_slope: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        regression = LinearRegression(tally=cmd.tally)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        prev_rec = None
        prev_value = None

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # rec...
            if cmd.iso not in paths:
                print("sample_slope: field %s not present." % cmd.iso, file=sys.stderr)
                exit(1)

            rec_node = datum.node(cmd.iso)
            rec = LocalizedDatetime.construct_from_iso8601(rec_node)

            if rec is None:
                print("sample_slope: invalid ISO 8601 value '%s' in %s." % (rec_node, jstr), file=sys.stderr)
                exit(1)

            # value...
            if cmd.path not in paths:
                print("sample_slope: field %s not present in %s." % (cmd.path, jstr), file=sys.stderr)
                exit(1)

            value_node = datum.node(cmd.path)
            value = Datum.float(value_node)

            if value is None:
                print("sample_slope: invalid numeric value '%s' in %s." % (value_node, jstr), file=sys.stderr)
                exit(1)

            # slope...
            regression.append(rec, value)

            if regression.has_regression():
                m, _ = regression.line()
                slope = None if m is None else round(m, cmd.precision)

            else:
                slope = None

            # target...
            target = PathDict()

            for path in datum.paths():
                if path == cmd.path:
                    target.append('.'.join((cmd.path, 'cur')), value)
                    target.append('.'.join((cmd.path, 'slope')), slope)
                    continue

                target.copy(datum, path)

            print(JSONify.dumps(target))
            sys.stdout.flush()

            prev_rec = rec
            prev_value = value
            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_slope: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
