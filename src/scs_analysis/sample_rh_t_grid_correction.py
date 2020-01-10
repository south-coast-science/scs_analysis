#!/usr/bin/env python3

"""
Created on 18 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_ah_correction utility is used to

SYNOPSIS
sample_rh_t_grid_correction.py -m B2 B1 B0 -c B2 B1 B0 [-r REFERENCE_PATH] [-v] RH_PATH T_PATH REPORT_SUB_PATH

EXAMPLES
csv_reader.py data.csv | \
sample_rh_t_grid_correction.py -v -m -0.001074 0.152974 -5.475746 -c -0.003792 0.846763 -22.535076 \
praxis.climate.val.hmd_m30 praxis.climate.val.tmp_p60 praxis.gas.val.NO2 | \
csv_writer.py corrected_data.csv

csv_reader.py data.csv | \
sample_rh_t_grid_correction.py -v -m -0.001074 0.152974 -5.475746 -c -0.003792 0.846763 -22.535076 -r ref.real \
praxis.climate.val.hmd_m30 praxis.climate.val.tmp_p60 praxis.gas.val.NO2

RESOURCES
https://joshualoong.com/2018/10/03/Fitting-Polynomial-Regressions-in-Python/
"""

import numpy as np
import scipy.stats as stats
import sys

from scs_analysis.cmd.cmd_sample_rh_t_grid_correction import CmdSampleRhTGridCorrection

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# TODO: use as the basis of gases exegesis

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

        cnc_report_path = cmd.report_sub_path + '.cnc'                  # '.weC_sens'          # '.cnc'
        sbl_report_path = cmd.report_sub_path + '.cnc_sbl1'             # '.weC_sens_sbl1'

        m_t_poly = np.poly1d(cmd.mt_weights)
        c_t_poly = np.poly1d(cmd.ct_weights)

        references = []
        corrected = []

        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

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
                report = float(datum.node(cnc_report_path))
            except (TypeError, ValueError):
                continue

            # numpy poly...
            m_t = m_t_poly(rh)
            c_t = c_t_poly(rh)

            # correction...
            error = (m_t * t) + c_t
            report_corrected = round(report - error, 1)

            if cmd.r2:
                try:
                    reference = float(datum.node(cmd.reference_path))
                except (TypeError, ValueError):
                    continue

                references.append(reference)
                corrected.append(report_corrected)

                continue

            # target...
            target = PathDict()

            for path in paths:
                target.append(path, datum.node(path))

                if path == cnc_report_path:
                    target.append(sbl_report_path, report_corrected)

            # data report...
            print(JSONify.dumps(target.node()))
            sys.stdout.flush()

        # r2 report...
        if cmd.r2:
            mt, ct, r, p, std_err = stats.linregress(references, corrected)
            print(round(r ** 2, 3))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyError as ex:
        print("sample_rh_t_grid_correction: KeyError: %s" % ex, file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_rh_t_grid_correction: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_rh_t_grid_correction: documents: %d" % document_count, file=sys.stderr)
