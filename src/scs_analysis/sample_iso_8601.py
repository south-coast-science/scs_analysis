#!/usr/bin/env python3

"""
Created on 15 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_iso_8601 utility is used to replace non-localised datetime fields with an ISO 8601 localised datetime field
for JSON documents of any schema.

Dates must be in the format YYY-MM-DD and times in the 24-hour format HH:MM or HH:MM:SS. For datetime fields, the format
may be YYY-MM-DD HH:MM or YYY-MM-DD HH:MM:SS. Hour values may exceed the range 0-23. If fields are missing from the
input document or are malformed, execution will terminate.

Output localised datetimes are always presented in UTC. If the input datetimes are not UTC, then the timezone of the
input data should be specified.

All fields in the input document are presented in the output document, with the exception of the selected date, time or
datetime fields. The default name for the ISO 8601 datetime output field is 'rec' but an alternate name may be
specified.

SYNOPSIS
sample_iso_8601.py { -z | [-i ISO_PATH] [-t TIMEZONE_NAME] [-v] { DATETIME_PATH | DATE_PATH TIME_PATH } }

EXAMPLES
csv_reader.py lhr_airwatch.csv | sample_iso_8601.py -t Europe/London Date Time

DOCUMENT EXAMPLE - INPUT
{"Date": "2019-01-31", "Time": "24:00:00", "NO2": {"dns": 29, "Status": "P ugm-3"},
"NO": {"dns": 54, "Status": "P ugm-3"}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2019-02-01T00:00:00Z", "NO2": {"dns": 29, "Status": "P ugm-3"}, "NO": {"dns": 54, "Status": "P ugm-3"}}

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
https://github.com/south-coast-science/scs_dev/wiki/3:-Data-formats
"""

import sys

from scs_analysis.cmd.cmd_sample_iso_8601 import CmdSampleISO8601

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict

from scs_core.location.timezone import Timezone


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    timezone = None
    zone = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleISO8601()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_iso_8601: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if cmd.timezone is not None:
            try:
                timezone = Timezone(cmd.timezone)
                zone = timezone.zone

            except ValueError:
                print("sample_iso_8601: unrecognised timezone:%s" % cmd.timezone, file=sys.stderr)
                exit(2)

            if cmd.verbose:
                print("sample_iso_8601: %s" % timezone, file=sys.stderr)
                sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.zones:
            for zone in Timezone.zones():
                print(zone, file=sys.stderr)
            exit(0)

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            paths = datum.paths()

            # date / time...
            if cmd.uses_datetime():
                if cmd.datetime_path not in paths:
                    print("sample_iso_8601: datetime path '%s' not in %s" % (cmd.datetime_path, jstr), file=sys.stderr)
                    exit(1)

                pieces = datum.node(cmd.datetime_path).split(' ')

                if len(pieces) != 2:
                    print("sample_iso_8601: malformed datetime '%s' in %s" % (cmd.datetime_path, jstr), file=sys.stderr)
                    exit(1)

                date = pieces[0]
                time = pieces[1]

            else:
                if cmd.date_path not in paths:
                    print("sample_iso_8601: date path '%s' not in %s" % (cmd.date_path, jstr), file=sys.stderr)
                    exit(1)

                if cmd.time_path not in paths:
                    print("sample_iso_8601: time path '%s' not in %s" % (cmd.time_path, jstr), file=sys.stderr)
                    exit(1)

                date = datum.node(cmd.date_path)
                time = datum.node(cmd.time_path)

            # ISO 8601...
            iso = LocalizedDatetime.construct_from_date_time(date, time, zone)

            if iso is None:
                print("sample_iso_8601: malformed datetime in %s" % jstr, file=sys.stderr)
                exit(1)

            if cmd.timezone is not None:
                iso = iso.utc()

            target = PathDict()
            target.append(cmd.iso, iso.as_iso8601())

            # copy...
            for path in paths:
                if path not in cmd.datetime_paths():
                    target.append(path, datum.node(path))

            # report...
            print(JSONify.dumps(target))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_iso_8601: KeyboardInterrupt", file=sys.stderr)
