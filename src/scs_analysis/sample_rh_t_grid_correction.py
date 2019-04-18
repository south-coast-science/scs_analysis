#!/usr/bin/env python3

"""
Created on 18 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
Important note: the equation applied by this utility is experimental.

The sample_ah_correction utility is used to

SYNOPSIS
sample_rh_t_grid_correction.py -m SLOPE INTERCEPT -c SLOPE INTERCEPT [-v] RH_PATH T_PATH REPORT_PATH

EXAMPLES

RESOURCES
https://joshualoong.com/2018/10/03/Fitting-Polynomial-Regressions-in-Python/
"""

import numpy as np
import sys

from scs_analysis.cmd.cmd_sample_rh_t_grid_correction import CmdSampleRhTGridCorrection

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleRhTGridCorrection()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_rh_t_grid_correction: %s" % cmd, file=sys.stderr)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        cnc_report_path = cmd.report_path + '.cnc'
        sbl_report_path = cmd.report_path + '.cnc-sbl1'

        m_t_poly = np.poly1d(cmd.mt_weights)
        c_t_poly = np.poly1d(cmd.ct_weights)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # nodes...
            rh_node = datum.node(cmd.rh_path)
            rh = float(rh_node)

            t_node = datum.node(cmd.t_path)
            t = float(t_node)

            report_node = datum.node(cnc_report_path)
            report = float(report_node)

            # numpy poly...
            m_t = m_t_poly(rh)
            c_t = c_t_poly(rh)

            # correction...
            error = (m_t * t) + c_t
            report_corrected = round(report - error, 1)

            # target...
            target = PathDict()

            for path in paths:
                target.append(path, datum.node(path))

                if path == cnc_report_path:
                    target.append(sbl_report_path, report_corrected)

            # report...
            print(JSONify.dumps(target.node()))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_rh_t_grid_correction: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_rh_t_grid_correction: documents: %d" % document_count, file=sys.stderr)
