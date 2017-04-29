#!/usr/bin/env python3

"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./localised_datetime.py -m -10
"""

import sys

from scs_core.data.localized_datetime import LocalizedDatetime

from scs_analysis.cmd.cmd_localised_datetime import CmdLocalizedDatetime

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdLocalizedDatetime()

    if cmd.verbose:
        print(cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    now = LocalizedDatetime.now()
    offset = now.timedelta(hours=cmd.hours, minutes=cmd.minutes, seconds=cmd.seconds)

    print(offset.as_iso8601())
