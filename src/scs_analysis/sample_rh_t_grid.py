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

Input documents whose temperature or humidity values are outside the specified bounds of the grid are ignored,
input documents with empty or non-floating point values will also be ignored.

SYNOPSIS
sample_rh_t_grid.py -r MIN MAX STEP -t MIN MAX STEP -o { R | C | M | S } [-v] RH_PATH T_PATH REPORT_PATH REF_PATH

EXAMPLES
csv_reader.py -v praxis_431_gases_2019-02-07_2019-03-14_15min_joined.csv | \
sample_rh_t_grid.py -v -r 0 100 10 -t 0 40 10 -o S val.sht.hmd.rH val.sht.tmp val.NO2.cnc '15 minute "real" data'

RESOURCES
https://joshualoong.com/2018/10/03/Fitting-Polynomial-Regressions-in-Python/
"""

import sys

from scs_analysis.cmd.cmd_sample_rh_t_grid import CmdSampleRhTGrid

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.error.error_grid import ErrorGrid

from scs_core.error.error_grid_report_rh_t import ErrorGridReportRhT
from scs_core.error.error_grid_report_t_rh import ErrorGridReportTRh
from scs_core.error.error_mesh_t_rh import ErrorMeshTRh
from scs_core.error.error_surface import ErrorSurface


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    included_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleRhTGrid()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_t_rh_grid: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        grid = ErrorGrid.construct(cmd.rh_min, cmd.rh_max, cmd.rh_step, cmd.t_min, cmd.t_max, cmd.t_step)

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

            # fields...
            try:
                rh = float(datum.node(cmd.rh_path))
            except (TypeError, ValueError):
                continue

            try:
                t = float(datum.node(cmd.t_path))
            except (TypeError, ValueError):
                continue

            try:
                report = float(datum.node(cmd.report_path))
            except (TypeError, ValueError):
                continue

            try:
                ref = float(datum.node(cmd.ref_path))
            except (TypeError, ValueError):
                continue

            # append...
            included = grid.append(rh, t, report, ref)

            if not included:
                if cmd.verbose:
                    print("sample_t_rh_grid: rejected: %s" % jstr, file=sys.stderr)
                    sys.stderr.flush()

                continue

            included_count += 1

        # report t rows...
        if cmd.output_mode == 'R':
            report = ErrorGridReportRhT.construct(grid)

            for row in report.rows():
                print(JSONify.dumps(row))

        # report t columns...
        elif cmd.output_mode == 'C':
            report = ErrorGridReportTRh.construct(grid)

            for row in report.rows():
                print(JSONify.dumps(row))

        # report mesh...
        elif cmd.output_mode == 'M':
            mesh = ErrorMeshTRh.construct(grid)

            for line in mesh.lines():
                print(JSONify.dumps(line))

        # report surface...
        elif cmd.output_mode == 'S':
            mesh = ErrorMeshTRh.construct(grid)
            surface = ErrorSurface.construct(mesh)

            print(JSONify.dumps(surface))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_t_rh_grid: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_t_rh_grid: documents: %d included: %d" % (document_count, included_count), file=sys.stderr)
