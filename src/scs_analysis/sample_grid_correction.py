#!/usr/bin/env python3

"""
Created on 1 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
Important note: the equation applied by this utility is experimental.

The sample_ah_correction utility is used to

SYNOPSIS
sample_ah_correction.py -s SENS_MV BASELINE -c WS WB [-v] GAS_SUB_PATH AH_PATH

EXAMPLES

"""

import json
import sys

from collections import OrderedDict

# from scs_analysis.cmd.cmd_sample_ah_correction import CmdSampleAhCorrection

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

# from scs_core.gas.ah_correction import AhCorrection


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    # hmd_path = 'praxis.val.sht.hmd.rH'
    # tmp_path = 'praxis.val.sht.tmp'
    #
    # report_path = 'praxis.val.NO2'

    # hmd_path = 'climate.val.hmd.m3m15'
    # tmp_path = 'climate.val.tmp.p2h'
    #
    # report_path = 'joined.praxis.val.NO2'

    hmd_path = 'praxis.climate.val.hmd_m225'
    tmp_path = 'praxis.climate.val.tmp_p145'

    report_path = 'praxis.gas.val.NO2'


    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # grid_jstr = '{' \
        #             '"50": {"5": null, "10": null, "15": 15.9, "20": 2.4, "25": -16.1, "30": -27.5}, ' \
        #             '"55": {"5": null, "10": null, "15": 15.1, "20": -3.6, "25": -19.4, "30": null}, ' \
        #             '"60": {"5": null, "10": 16.4, "15": 14.8, "20": -0.9, "25": null, "30": null}, ' \
        #             '"65": {"5": null, "10": 13.9, "15": 13.9, "20": 7.3, "25": null, "30": null}, ' \
        #             '"70": {"5": null, "10": 18.8, "15": 13.9, "20": 13.2, "25": null, "30": null}, ' \
        #             '"75": {"5": null, "10": 17.0, "15": 16.1, "20": 19.3, "25": null, "30": null}, ' \
        #             '"80": {"5": 18.9, "10": 19.5, "15": 15.7, "20": null, "25": null, "30": null}, ' \
        #             '"85": {"5": 23.2, "10": 20.5, "15": 16.6, "20": null, "25": null, "30": null}, ' \
        #             '"90": {"5": null, "10": 22.3, "15": 18.3, "20": null, "25": null, "30": null}}'

        # grid_jstr = '{"25": {"5": null, "10": null, "15": -29.2, "20": -45.2, "25": null, "30": null}, ' \
        #             '"30": {"5": null, "10": -20.5, "15": -15.4, "20": -38.8, "25": null, "30": null}, ' \
        #             '"35": {"5": null, "10": -18.2, "15": -20.7, "20": -28.8, "25": -33.4, "30": null}, ' \
        #             '"40": {"5": null, "10": 1.6, "15": 9.5, "20": -26.9, "25": -25.6, "30": 5.6}, ' \
        #             '"45": {"5": null, "10": 0.7, "15": 7.6, "20": -30.5, "25": 6.4, "30": 11.8}, ' \
        #             '"50": {"5": null, "10": 2.1, "15": 8.2, "20": -6.7, "25": 0.5, "30": null}, ' \
        #             '"55": {"5": 11.6, "10": 11.0, "15": 7.9, "20": 2.2, "25": -2.6, "30": null}, ' \
        #             '"60": {"5": null, "10": 14.3, "15": 15.0, "20": 8.6, "25": 8.1, "30": null}, ' \
        #             '"65": {"5": 17.1, "10": 17.6, "15": 12.9, "20": 13.3, "25": 12.4, "30": null}, ' \
        #             '"70": {"5": 16.0, "10": 20.9, "15": 16.4, "20": 13.1, "25": 7.1, "30": null}, ' \
        #             '"75": {"5": 20.5, "10": 18.9, "15": 14.1, "20": 14.4, "25": 10.2, "30": null}, ' \
        #             '"80": {"5": null, "10": 20.4, "15": 17.0, "20": 22.1, "25": null, "30": null}, ' \
        #             '"85": {"5": null, "10": 20.3, "15": 18.1, "20": 19.8, "25": null, "30": null}, ' \
        #             '"90": {"5": null, "10": 20.1, "15": 19.8, "20": null, "25": null, "30": null}}'
        #
        # str_grid = json.loads(grid_jstr)
        #
        # grid = OrderedDict()
        #
        # for hmd_boundary in str_grid.keys():
        #     grid[int(hmd_boundary)] = OrderedDict()
        #
        #     for tmp_boundary in str_grid[hmd_boundary].keys():
        #         grid[int(hmd_boundary)][int(tmp_boundary)] = str_grid[hmd_boundary][tmp_boundary]
        #
        # print("sample_grid_correction: %s" % grid, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # print("paths: %s" % paths, file=sys.stderr)

            hmd_node = datum.node(hmd_path)
            hmd = float(hmd_node)

            tmp_node = datum.node(tmp_path)
            tmp = float(tmp_node)

            report_node = datum.node(report_path + '.cnc')
            report = float(report_node)

            # find correction...
            # g_correction = None
            #
            # for hmd_boundary in grid.keys():
            #     if hmd < hmd_boundary:
            #         for tmp_boundary in grid[hmd_boundary].keys():
            #             if tmp < tmp_boundary:
            #                 g_correction = grid[hmd_boundary][tmp_boundary]
            #                 break
            #         break
            #
            # if g_correction is None:
            #     print("sample_grid_correction: no value for tmp:%s hmd:%s" % (tmp, hmd), file=sys.stderr)
            #     g_corrected = None
            #
            # else:
            #     g_corrected = round(report - g_correction, 1)

            # grid1...
            # m_t = (0.0693 * hmd) - 6.0615
            # c_t = (-0.9246 * hmd) + 98.117

            # grid2...
            # m_t = (0.0844 * hmd) - 6.7187
            # c_t = (-1.0479 * hmd) + 98.792

            # grid2 climate...
            # m_t = (0.0705 * hmd) - 5.5402
            # c_t = (-0.625 * hmd) + 70.941

            # poly climate...
            # m_t = (-0.0008 * hmd * hmd) + (0.1665 * hmd) - 8.1832
            # c_t = (0.0231 * hmd * hmd) - (3.3965 * hmd) + 147.21

            # poly climate ts2h...
            # m_t = (0.0006 * hmd * hmd) - (0.0547 * hmd) + 1.0142
            # c_t = (-0.0249 * hmd * hmd) + (3.4275 * hmd) - 101.58

            # poly climate ts3h...
            # m_t = (-0.0009 * hmd * hmd) + (0.1231 * hmd) - 4.3593
            # c_t = (-0.0123 * hmd * hmd) + (1.9361 * hmd) - 55.81

            # poly climate ts4h...
            # m_t = (-0.0007 * hmd * hmd) + (0.1153 * hmd) - 4.6771
            # c_t = (-0.005 * hmd * hmd) + (0.92 * hmd) - 20.085

            # poly climate ts3p5h...
            # m_t = (-0.0005 * hmd * hmd) + (0.0871 * hmd) - 3.7504
            # c_t = (-0.0078 * hmd * hmd) + (1.2619 * hmd) - 31.886

            # poly climate ts h m3m15...
            # m_t = (-0.0011 * hmd * hmd) + (0.1512 * hmd) - 5.1792
            # c_t = (-0.0003 * hmd * hmd) + (0.4465 * hmd) - 12.373

            # praxis_tp145_rhm225_LHR2_ref_15_min_rec...
            # m_t = (-0.0011 * hmd * hmd) + (0.153 * hmd) - 5.4757
            # c_t = (-0.00038 * hmd * hmd) + (0.8468 * hmd) - 22.535

            # praxis_tp145_rhm225_LHR2_ref_15_min_rec linear...
            # m_t = (0.0295 * hmd) - 2.4264
            # c_t = (0.4107 * hmd) - 11.768

            # praxis_tp145_rhm225_LHR2_ref_15_min_rec categorical...
            m_t = (0.1474 * hmd) - 1.9105
            c_t = (2.0536 * hmd) - 4.5807

            r_correction = (m_t * tmp) + c_t
            r_corrected = round(report - r_correction, 1)

            # print("t: %5.1f rh: %5.1f g_corr: %s r_corr: %0.3f" % (tmp, hmd, g_correction, r_correction),
            #       file=sys.stderr)

            print("t: %5.1f rh: %5.1f r_corr: %0.3f" % (tmp, hmd, r_correction),
                  file=sys.stderr)

            # copy...
            target = PathDict()

            for path in paths:
                target.append(path, datum.node(path))

                if path == report_path + '.cnc':
                    # target.append(report_path + '.gcorr', g_corrected)
                    target.append(report_path + '.rcorr', r_corrected)

            # report...
            print(JSONify.dumps(target.node()))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        pass

    finally:
        print("sample_grid_correction: documents: %d processed: %d" % (document_count, processed_count),
              file=sys.stderr)
