#!/usr/bin/env python3

"""
Created on 16 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./socket_receiver.py | ./sample_interval.py rec
"""

import sys

from scs_analysis.cmd.cmd_sample_interval import CmdSampleInterval

from scs_core.data.interval import Interval
from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict
from scs_core.sys.exception_report import ExceptionReport


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleInterval()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)
        sys.stderr.flush()


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        prev_time = None

        for line in sys.stdin:
            if cmd.verbose:
                print(line, file=sys.stderr)

            sample_datum = PathDict.construct_from_jstr(line)

            if sample_datum is None:
                break

            time = LocalizedDatetime.construct_from_iso8601(sample_datum.node(cmd.path))

            interval = Interval.construct(prev_time, time, cmd.precision)
            print(JSONify.dumps(interval))

            prev_time = time


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_interval: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
