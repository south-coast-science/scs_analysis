#!/usr/bin/env python3

"""
Created on 16 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_t_rh_grid utility is used to group gas concentration errors according to temperature and relative humidity.

The utility generates a grid of temperature / humidity deltas, then appends each pair of reference and reported values
into the sample group of the appropriate cell. When all input documents have been processed, the utility outputs
the grid, indicating the number of values and, where possible, the average and standard deviation for each cell.

The output grid may have rows for humidity steps and columns for temperature steps, or vice-versa. Alternatively, the
utility may simply report the average standard deviation for all cells.

Input documents whose temperature or humidity values are outside the specified bounds of the grid are ignored.
Missing or non-floating point values will cause the utility to terminate.

SYNOPSIS
sample_t_rh_grid.py -r MIN MAX STEP -t MIN MAX STEP { -w | -c | -d } [-v] RH_PATH T_PATH REPORT_PATH, REF_PATH

EXAMPLES
csv_reader.py praxis_ref_joined_climate_tsh3m15.csv | \
sample_t_rh_grid.py -r 20 95 5 -t 0 30 5 -d -v climate.val.hmd.rH climate.val.tmp.C \
joined.praxis.val.NO2.cnc joined.ref.15min
"""

import sys

from scs_analysis.cmd.cmd_sample_t_rh_grid import CmdSampleTRhGrid

from scs_core.data.json import JSONify
from scs_core.data.error_grid import ErrorGridRhT, ErrorGridTRh
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    included_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleTRhGrid()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_t_rh_grid: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if cmd.rh_cols:
            grid = ErrorGridTRh.construct(cmd.rh_min, cmd.rh_max, cmd.rh_step, cmd.t_min, cmd.t_max, cmd.t_step)

        else:
            grid = ErrorGridRhT.construct(cmd.rh_min, cmd.rh_max, cmd.rh_step, cmd.t_min, cmd.t_max, cmd.t_step)

        if cmd.verbose:
            print(grid, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # input...
        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            # nodes...
            rh_node = datum.node(cmd.rh_path)
            rh = float(rh_node)

            t_node = datum.node(cmd.t_path)
            t = float(t_node)

            report_node = datum.node(cmd.report_path)
            report = float(report_node)

            ref_node = datum.node(cmd.ref_path)
            ref = float(ref_node)

            # append...
            included = grid.append(rh, t, report, ref)

            if not included:
                if cmd.verbose:
                    print("sample_t_rh_grid: rejected: %s" % jstr, file=sys.stderr)
                    sys.stderr.flush()

                continue

            included_count += 1

        # report...
        if cmd.stdev:
            print(grid.stdev())

        else:
            for row in grid.as_json():
                print(JSONify.dumps(row))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_t_rh_grid: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_t_rh_grid: documents: %d included: %d" % (document_count, included_count),
                  file=sys.stderr)
