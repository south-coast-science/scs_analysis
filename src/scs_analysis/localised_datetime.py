#!/usr/bin/env python3

"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The localised_datetime utility is used to report the localised date and time, as understood by the host operating
system, in ISO 8601 format. It can also report date / time offset by a given number of hours, minutes and seconds.

Optional offsets in hours, minutes and seconds can be supplied.

The utility is useful when composing topic history data requests.

SYNOPSIS
localised_datetime.py [-o HOURS] [-m MINUTES] [-s SECONDS]

EXAMPLES
./localised_datetime.py -o 1

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
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
