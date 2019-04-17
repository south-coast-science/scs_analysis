#!/usr/bin/env python3

"""
Created on 1 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_ah_correction utility is used to

SYNOPSIS
sample_ah_correction.py -s SENS_MV BASELINE -c WS WB [-v] GAS_SUB_PATH AH_PATH

EXAMPLES

DOCUMENT EXAMPLE - INPUT

DOCUMENT EXAMPLE - OUTPUT
"""

import sys


# from collections import OrderedDict

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.data.error_grid import ErrorGridTRh


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    hmd_boundaries = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]
    hmd_lower_bound = 20

    tmp_boundaries = [5, 10, 15, 20, 25, 30]
    tmp_lower_bound = 0

    # hmd_path = 'praxis.val.sht.hmd'
    # tmp_path = 'praxis.val.sht.tmp'

    # report_path = 'praxis.val.NO2.cnc'
    # actual_path = 'ref.15 minute "real" data'

    hmd_path = 'climate.val.hmd.rH'
    tmp_path = 'climate.val.tmp.C'

    # hmd_path = 'climate.val.hmd.m3m15'
    # tmp_path = 'climate.val.tmp.p2h'

    report_path = 'joined.praxis.val.NO2.cnc'
    actual_path = 'joined.ref.15 minute "real" data'

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # grid = ErrorGridRhT.construct(20, 95, 5, 0, 30, 5)
        grid = ErrorGridTRh.construct(20, 95, 5, 0, 30, 5)

        print(grid, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            hmd_node = datum.node(hmd_path)
            hmd = float(hmd_node)

            tmp_node = datum.node(tmp_path)
            tmp = float(tmp_node)

            report_node = datum.node(report_path)
            report = float(report_node)

            actual_node = datum.node(actual_path)
            actual = float(actual_node)

            # print("hmd: %s tmp: %s report: %s actual: %s" % (hmd, tmp, report, actual))

            # total.append(report, actual)

            included = grid.append(hmd, tmp, report, actual)

            if included:
                processed_count += 1

            else:
                print("rejected: %s" % jstr, file=sys.stderr)

        # low = total.lowest_error()
        # avg = total.avg_error()
        # high = total.highest_error()

        # print("all: %4d  low error: %s  avg error: %s  high error: %s" %
        #       (processed_count, low, avg, high))

        total = 0

        # for hmd_boundary, tmp_row in grid.items():
        #     for tmp_boundary, tmp_group in tmp_row.items():
        #         low = tmp_group.lowest_error()
        #         avg = tmp_group.avg_error()
        #         high = tmp_group.highest_error()
        #
        #         print("hmd: %4.1f  tmp: %4.1f  len: %4d  low error: %s  avg error: %s  high error: %s" %
        #               (hmd_boundary, tmp_boundary, len(tmp_group), low, avg, high))
        #
        #         total += len(tmp_group)
        #
        #     print("-")

        # print("total: %s" % total)

        for row in grid.as_json():
            print(JSONify.dumps(row))

        print("stdev: %s" % grid.stdev(), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        pass

    finally:
        print("gridalyser: documents: %d processed: %d" % (document_count, processed_count),
              file=sys.stderr)
