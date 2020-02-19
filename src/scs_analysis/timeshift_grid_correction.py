#!/usr/bin/env python3

"""
Created on 18 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The timeshift_grid_correction utility is used to

SYNOPSIS
timeshift_grid.py -r START END STEP -t START END STEP -p FILENAME -f FILENAME [-v] RH_PATH T_PATH REPORT_PATH REF_PATH

EXAMPLES
timeshift_grid.py -v -r -240 -180 5 -t 120 120 1 -p praxis_climate_joined_1min.csv -f LHR2_ref_15_min_rec.csv \
climate.val.hmd climate.val.tmp gas.val.NO2 real
"""

import json
import sys
import time

from scs_analysis.cmd.cmd_timeshift_grid_correction import CmdTimeshiftGridCorrection

from scs_core.error.error_surface import ErrorSurface
from scs_core.sys.subprocess import Pipe


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdTimeshiftGridCorrection()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("timeshift_grid: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # TODO: use the original filename prefixes...

        # files...
        reported_t_shifted_filename = 'timeshift_grid_t_shifted_tmp.csv'
        reported_15min_filename = 'timeshift_grid_15min_tmp.csv'
        joined_15min_filename = 'timeshift_grid_joined_tmp.csv'

        # paths...
        report_prefix = 'praxis'
        ref_prefix = 'ref'

        joined_report_sub_path = '.'.join((report_prefix, cmd.report_sub_path))
        joined_report_path = joined_report_sub_path + '.weC_sens'

        joined_ref_path = '.'.join((ref_prefix, cmd.ref_path))


        # ------------------------------------------------------------------------------------------------------------
        # run...

        offset_infix = 'm' if cmd.t_offset < 0 else 'p'
        t_shifted_path = cmd.t_path + '_' + offset_infix + str(abs(cmd.t_offset))

        praxis_t_shifted_path = 'praxis.' + t_shifted_path


        # ----------------------------------------------------------------------------------------------------
        # run: time shift t 1 min data, compute weC_sens...

        if cmd.verbose:
            print("timeshift_grid_correction: time shift t 1 min data, compute weC_sens...", end='',
                  file=sys.stderr)
            sys.stderr.flush()

        p = Pipe(('csv_reader.py', cmd.report_filename),
                 ('node_shift.py', '-o', cmd.t_offset, cmd.t_path, t_shifted_path),
                 ('sample_wec_sens.py', t_shifted_path, cmd.report_sub_path),
                 ('csv_writer.py', reported_t_shifted_filename))

        return_code = p.wait()

        if return_code > 0:
            print("timeshift_grid_correction: t shift phase failed with exit code %s." % return_code,
                  file=sys.stderr)
            exit(return_code)

        if cmd.verbose:
            print("done.", file=sys.stderr)


        # --------------------------------------------------------------------------------------------------------

        offset_infix = 'm' if cmd.rh_offset < 0 else 'p'
        rh_shifted_path = cmd.rh_path + '_' + offset_infix + str(abs(cmd.rh_offset))

        praxis_rh_shifted_path = 'praxis.' + rh_shifted_path

        start_time = time.time()


        # ----------------------------------------------------------------------------------------------------
        # run: time shift rH 1 min data, aggregate to 15 min...

        if cmd.verbose:
            print("timeshift_grid_correction: time shift rH 1 min data, aggregate to 15 min...", end='',
                  file=sys.stderr)
            sys.stderr.flush()

        p = Pipe(('csv_reader.py', reported_t_shifted_filename),
                 ('node_shift.py', '-o', cmd.rh_offset, cmd.rh_path, rh_shifted_path),
                 ('sample_aggregate.py', '-c' '**:/15:00'),
                 ('csv_writer.py', reported_15min_filename))

        return_code = p.wait()

        if return_code > 0:
            print("timeshift_grid_correction: rH shift phase failed with exit code %s." % return_code,
                  file=sys.stderr)
            exit(return_code)

        if cmd.verbose:
            print("done.", file=sys.stderr)


        # -----------------------------------------------------------------------------------------------------
        # run: join with ref 15 min data...

        if cmd.verbose:
            print("timeshift_grid_correction: join with ref 15 min data...", end='',
                  file=sys.stderr)
            sys.stderr.flush()

        p = Pipe(('csv_join.py', '-i', '-l', report_prefix, 'rec', reported_15min_filename,
                  '-r', ref_prefix, 'rec', cmd.ref_filename),
                 ('csv_writer.py', joined_15min_filename))

        return_code = p.wait()

        if return_code > 0:
            print("timeshift_grid_correction: join phase failed with exit code %s." % return_code,
                  file=sys.stderr)
            exit(return_code)

        if cmd.verbose:
            print("done.", file=sys.stderr)


        # ----------------------------------------------------------------------------------------------------
        # run: t rH grid...

        if cmd.verbose:
            print("timeshift_grid_correction: t rH grid...", end='',
                  file=sys.stderr)
            sys.stderr.flush()

        p = Pipe(('csv_reader.py', joined_15min_filename),
                 ('sample_rh_t_grid.py', '-r', 20, 95, 5, '-t', 0, 30, 5, '-o', 'S',
                  praxis_rh_shifted_path, praxis_t_shifted_path, joined_report_path, joined_ref_path))

        output = p.check_output()

        if cmd.verbose:
            print("done.", file=sys.stderr)
            sys.stderr.flush()

        s = ErrorSurface.construct_from_jdict(json.loads(output))

        print("output: %s" % output, file=sys.stderr)
        print("surface: %s" % s, file=sys.stderr)


        # ----------------------------------------------------------------------------------------------------
        # run: correction...

        if cmd.verbose:
            print("timeshift_grid_correction: correction...", end='',
                  file=sys.stderr)

        p = Pipe(('csv_reader.py', joined_15min_filename),
                 ('sample_rh_t_grid_correction.py',
                  '-m', s.mt_weight_b2, s.mt_weight_b1, s.mt_weight_b0,
                  '-c', s.ct_weight_b2, s.ct_weight_b1, s.ct_weight_b0,
                  praxis_rh_shifted_path, praxis_t_shifted_path, joined_report_sub_path))

        return_code = p.wait()

        if return_code > 0:
            print("timeshift_grid_correction: correction phase failed with exit code %s." % return_code,
                  file=sys.stderr)
            exit(return_code)

        if cmd.verbose:
            print("done.", file=sys.stderr)
            sys.stderr.flush()

        # TODO: delete rh tmp files

        # TODO: delete t tmp file


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("timeshift_grid_correction: KeyboardInterrupt", file=sys.stderr)
