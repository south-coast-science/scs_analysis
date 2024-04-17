#!/usr/bin/env python3

"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The localised_datetime utility is used to report the localised date and time, as understood by the host operating
system, in ISO 8601 format. Optional offsets in hours, minutes and seconds can be supplied.

The utility is useful when composing topic history data requests, or just finding out what the time is somewhere else.

SYNOPSIS
localised_datetime.py { [-o HOURS] [-m MINUTES] [-s SECONDS] [-t TIMEZONE_NAME] | -z }

EXAMPLES
localised_datetime.py -t Europe/Athens
localised_datetime.py -o 2

DOCUMENT EXAMPLE - OUTPUT
2018-04-05T18:42:03.702+00:00

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys

from scs_analysis.cmd.cmd_localised_datetime import CmdLocalizedDatetime

from scs_core.data.datetime import LocalizedDatetime

from scs_core.location.timezone import Timezone


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdLocalizedDatetime()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("localised_datetime: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    if cmd.list:
        for zone in Timezone.zones():
            print(zone, file=sys.stderr)
        exit(0)

    now = LocalizedDatetime.now()
    ldt = now.timedelta(hours=cmd.hours, minutes=cmd.minutes, seconds=cmd.seconds)

    if cmd.zone is not None:
        if not Timezone.is_valid(cmd.zone):
            print("localised_datetime: invalid timezone: %s" % cmd.zone, file=sys.stderr)
            exit(1)

        timezone = Timezone(cmd.zone)
        ldt = ldt.localize(timezone.zone)

    report = ldt.as_readable() if cmd.readable else ldt.as_iso8601()

    print(report)
