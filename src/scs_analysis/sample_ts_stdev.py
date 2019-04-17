#!/usr/bin/env python3

"""
Created on 16 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_ts_stdev utility is used to

SYNOPSIS


EXAMPLES

"""

import sys
import time

from collections import OrderedDict

from subprocess import check_output, Popen, PIPE

from scs_analysis.cmd.cmd_sample_rh_t_grid import CmdSampleRhTGrid

from scs_core.data.error_report import ErrorReport
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    praxis_1min_filename = 'praxis_climate_joined_1min_tp145.csv'
    praxis_15min_filename = 'praxis_climate_joined_tp145_hmX_15min.csv'

    # praxis_1min_filename = 'praxis_climate_joined_1min_hm230.csv'
    # praxis_15min_filename = 'praxis_climate_joined_tpX_hm230_15min.csv'

    ref_15min_filename = 'LHR2_ref_15_min_rec.csv'

    joined_15min_filename = 'praxis_shifted_LHR2_ref_15_min_rec.csv'

    rh_path = 'climate.val.hmd'
    # rh_path = 'climate.val.hmd_m230'
    # t_path = 'climate.val.tmp'

    rh_ts_offset_min = -360
    rh_ts_offset_max = -60
    rh_ts_offset_step = 5

    t_ts_offset_min = 30
    t_ts_offset_max = 180
    t_ts_offset_step = 5

    t_ts = 145

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # stdevs = OrderedDict()

        # for rh_ts in range(rh_ts_offset_min, rh_ts_offset_max + 1, rh_ts_offset_step):
        #     stdevs[rh_ts] = OrderedDict()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        t_ts_path = 'climate.val.tmp_p145'

        # rh_ts = -230

        for rh_ts in range(rh_ts_offset_min, rh_ts_offset_max + 1, rh_ts_offset_step):
        # for t_ts in range(t_ts_offset_min, t_ts_offset_max + 1, t_ts_offset_step):

            start_time = time.time()

            rh_ts_path = 'climate.val.hmd_m' + str(abs(rh_ts))

            # t_ts_path = 'climate.val.tmp_p' + str(abs(t_ts))

            # --------------------------------------------------------------------------------------------------------
            # run: time shift 1 min data, aggregate to 15 min...

            if True:
                print("sample_ts_stdev: time shift 1 min data, aggregate to 15 min...", end='', file=sys.stderr)
                sys.stderr.flush()

            args = ['csv_reader.py', praxis_1min_filename]
            sp1 = Popen(args, stdout=PIPE)

            args = ['node_shift.py', '-o', str(rh_ts), rh_path, rh_ts_path]
            # args = ['node_shift.py', '-o', str(t_ts), t_path, t_ts_path]

            sp2 = Popen(args, stdin=sp1.stdout, stdout=PIPE)

            args = ['sample_aggregate.py', '-c' '**:/15:00']
            sp3 = Popen(args, stdin=sp2.stdout, stdout=PIPE)

            args = ['csv_writer.py', praxis_15min_filename]
            sp4 = Popen(args, stdin=sp3.stdout)

            sp4.wait()

            if sp4.returncode > 0:
                print("sample_ts_stdev: shift failed with exit code %s." % sp4.returncode, file=sys.stderr)
                exit(sp4.returncode)

            if True:
                print("done.", file=sys.stderr)


            # --------------------------------------------------------------------------------------------------------
            # run: join with ref 15 min data...

            if True:
                print("sample_ts_stdev: join with ref 15 min data...", end='', file=sys.stderr)
                sys.stderr.flush()

            args = ['csv_join.py', '-i', '-l', 'praxis', 'rec', praxis_15min_filename,
                    '-r', 'ref', 'rec', ref_15min_filename]
            sp1 = Popen(args, stdout=PIPE)

            args = ['csv_writer.py', joined_15min_filename]
            sp2 = Popen(args, stdin=sp1.stdout)

            sp2.wait()

            if sp2.returncode > 0:
                print("sample_ts_stdev: join failed with exit code %s." % sp2.returncode, file=sys.stderr)
                exit(sp2.returncode)

            if True:
                print("done.", file=sys.stderr)


            # --------------------------------------------------------------------------------------------------------
            # run: t rH grid...

            if True:
                print("sample_ts_stdev: t rH grid...", end='', file=sys.stderr)
                sys.stderr.flush()

            args = ['csv_reader.py', joined_15min_filename]
            sp1 = Popen(args, stdout=PIPE)

            args = ['sample_rh_t_grid.py', '-r', '20', '95', '5', '-t', '0', '30', '5', '-d',
                    'praxis.' + rh_ts_path, 'praxis.' + t_ts_path, 'praxis.gas.val.NO2.cnc', 'ref.real']
            # args = ['sample_t_rh_grid.py', '-r', '20', '95', '5', '-t', '0', '30', '5', '-d',
            #         'praxis.' + rh_path, 'praxis.' + t_ts_path, 'praxis.gas.val.NO2.cnc', 'ref.real']

            output = check_output(args, stdin=sp1.stdout)

            stdev = float(output.decode())

            if sp2.returncode > 0:
                print("sample_ts_stdev: grid failed with exit code %s." % sp2.returncode, file=sys.stderr)
                exit(sp2.returncode)

            if True:
                print("done.", file=sys.stderr)


            # --------------------------------------------------------------------------------------------------------
            # run: report...

            elapsed_time = round(time.time() - start_time, 1)
            print("elapsed: %s" % elapsed_time, file=sys.stderr)

            report = ErrorReport(t_ts, rh_ts, stdev)
            print(JSONify.dumps(report))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print("sample_ts_stdev: KeyboardInterrupt", file=sys.stderr)
