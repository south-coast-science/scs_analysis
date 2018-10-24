#!/usr/bin/env python3

"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The localised_datetime utility is used to report the localised date and time, as understood by the host operating
system, in ISO 8601 format. Optional offsets in hours, minutes and seconds can be supplied.

The utility is useful when composing topic history data requests.

SYNOPSIS
localised_datetime.py [-o HOURS] [-m MINUTES] [-s SECONDS]

EXAMPLES
localised_datetime.py -o 1

DOCUMENT EXAMPLE - OUTPUT
2018-04-05T18:42:03.702+00:00

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys

from scs_analysis.cmd.cmd_localised_datetime import CmdLocalizedDatetime

from scs_core.data.localized_datetime import LocalizedDatetime


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdLocalizedDatetime()

    if cmd.verbose:
        print("localised_datetime: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    now = LocalizedDatetime.now()
    offset = now.timedelta(hours=cmd.hours, minutes=cmd.minutes, seconds=cmd.seconds)

    print(offset.as_iso8601())
