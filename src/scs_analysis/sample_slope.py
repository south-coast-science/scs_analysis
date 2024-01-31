#!/usr/bin/env python3

"""
Created on 23 Oct 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_slope utility it used to find the slope for a given field in a sequence of JSON documents. Slope is
defined as delta value / delta time (in seconds).

The output document replaced the input field with field.cur (the current value) and field.slope. For the initial
input document, the corresponding output document's field.slope value is null. A --tally flag specifies the number
of rolling samples in the regression.

The --max-interval flag is intended to prevent slope analyses covering long periods such as device downtime.

If the --exclude-incomplete flag is set, then any data proir to the required number of tallies is not output. Where
a chain of slope analyses are being performed, the flag should only be used on the last (highest tally) pass.

SYNOPSIS
sample_slope.py -n NAME [-i ISO] [-t TALLY] [-m [DD-]HH:MM[:SS]] [-x] [-p PRECISION] [-v] PATH

EXAMPLES
bruno:scs-opc-164 bruno$ csv_reader.py -v scs-opc-164-meteo-pmx-2022-15min.csv | \
sample_slope.py -v -n 15min -t2 -m 00:15:00 -x meteo.val.hmd | \
csv_writer.py -v scs-opc-164-meteo-pmx-2022-15min-slope.csv

DOCUMENT EXAMPLE - INPUT
{"rec": "2022-09-13T13:30:00Z", "val": {"hmd": 72.5, "tmp": 22.2,
"bar": {"pA": 100.964}}, "ver": 1.0, "tag": "scs-opc-125"}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2022-09-13T13:30:00Z", "val": {"hmd": {"cur": 72.5, "slp15min": -0.000111, "slp30min": 0.0005},
"tmp": 22.2, "bar": {"pA": 100.964}}, "ver": 1.0, "tag": "scs-opc-125"}
"""

import sys

from scs_analysis.cmd.cmd_sample_slope import CmdSampleSlope

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.datum import Datum
from scs_core.data.json import JSONify
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.path_dict import PathDict

from scs_core.sys.logging import Logging


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

    Logging.config('sample_slope', verbose=cmd.verbose)
    logger = Logging.getLogger()

    if not cmd.is_valid_interval():
        logger.error("invalid format for max interval.")
        exit(2)

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        regression = LinearRegression(tally=cmd.tally)

        source_path = cmd.path

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
                logger.error("field %s not present." % cmd.iso)
                exit(1)

            rec_node = datum.node(cmd.iso)
            rec = LocalizedDatetime.construct_from_iso8601(rec_node)

            if rec is None:
                logger.error("invalid ISO 8601 value '%s' in %s." % (rec_node, jstr))
                exit(1)

            # exclude long intervals...
            if cmd.max_interval and prev_rec is not None and rec - prev_rec > cmd.max_interval:
                logger.info("regression reset on %s" % jstr)
                regression.reset()

            # value...
            if source_path not in paths:
                if source_path + '.cur' in paths:
                    source_path += '.cur'               # we are extending an existing slope analysis
                else:
                    logger.error("field %s not present in %s." % (cmd.path, jstr))
                    exit(1)

            value_node = datum.node(source_path)
            value = Datum.float(value_node)

            if value is None:
                logger.error("invalid numeric value '%s' in %s." % (value_node, jstr))
                exit(1)

            # slope...
            regression.append(rec, value)

            if regression.has_regression():
                slope = regression.slope(precision=cmd.precision)

            else:
                slope = None

            # target...
            target = PathDict()

            for path in datum.paths():
                if path == source_path:
                    target.append('.'.join((cmd.path, 'cur')), value)
                    target.append('.'.join((cmd.path, 'slp' + cmd.name)), slope)
                    continue

                target.copy(datum, path)

            prev_rec = rec
            prev_value = value

            if cmd.exclude_incomplete and (slope is None or document_count < cmd.tally):
                continue

            print(JSONify.dumps(target))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        logger.info("documents: %d processed: %d" % (document_count, processed_count))
