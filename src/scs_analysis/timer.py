#!/usr/bin/env python3

"""
Created on 11 Feb 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The timer utility is used to report elapsed time for a command line job. To use, it should be threaded into a pipeline,
where it passes stdin to stout. On terminating, the timer utility reports a timedelta to stderr.

SYNOPSIS
timer.py

EXAMPLES
csv_reader.py source*.csv | timer.py | csv_writer.py target.csv
"""

import sys
import time

from scs_core.data.json import JSONify
from scs_core.data.timedelta import Timedelta


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    print("timer: starting", file=sys.stderr)
    sys.stderr.flush()

    start_time = time.time()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            print(line, end='')
            sys.stdout.flush()

    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print("timer: KeyboardInterrupt", file=sys.stderr)

    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        elapsed_time = time.time() - start_time
        delta = Timedelta(seconds=elapsed_time)

        print("timer: %s" % JSONify.dumps(delta.as_json()).strip('"'), file=sys.stderr)
