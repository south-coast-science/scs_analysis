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

https://stackoverflow.com/questions/26692284/how-to-prevent-brokenpipeerror-when-doing-a-flush-in-python
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.timedelta import Timedelta

from scs_core.sys.logging import Logging
from scs_core.sys.timer import Timer


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    Logging.config('timer', verbose=True)
    logger = Logging.getLogger()

    logger.info("starting")

    timer = Timer()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            print(line, end='')
            sys.stdout.flush()

    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except (BrokenPipeError, IOError):
        pass

    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        delta = Timedelta(seconds=int(round(timer.total())))
        logger.info(JSONify.dumps(delta).strip('"'))

        sys.stderr.close()
