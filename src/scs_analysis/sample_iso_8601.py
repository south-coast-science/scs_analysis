#!/usr/bin/env python3

"""
Created on 15 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_iso_8601 utility is used to replace non-localised datetime fields with an ISO 8601 localised datetime field
for JSON documents of any schema.

Dates may be in the format:

* DD-MM-YYYY
* DD/MM/YYYY
* DD/MM/YY
* DD_MMM_YYYY
* MM-DD-YYYY
* MM/DD/YYYY
* MM/DD/YY
* YYYY-MM-DD
* YYYY/MM/DD
* OLE Automation date

Times in the 24-hour format HH:MM or HH:MM:SS. For datetime fields, the
format may be YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS. Hour values may exceed the range 0-23. If fields are missing
from the input document or are malformed, execution will terminate.

If the input datetimes are not UTC, then the timezone of the input data should be specified. In this case, the
datetime may optionally be shifted to UTC.

All fields in the input document are presented in the output document, with the exception of the selected date, time or
datetime fields. The default name for the ISO 8601 datetime output field is 'rec' but an alternate name may be
specified.

SYNOPSIS
sample_iso_8601.py { -z | { -o | -f DATE_FORMAT } [-t TIMEZONE_NAME [-u]] [-i ISO_PATH]
{ DATETIME_PATH | DATE_PATH TIME_PATH } } [-v]

EXAMPLES
csv_reader.py 15_min_Praxis_LHR2.csv -l10 | sample_iso_8601.py -v -f DD/MM/YYYY "Max of Time" -t Europe/Athens -u

DOCUMENT EXAMPLE - INPUT
{"Max of Time": "08/02/2019 00:00", "Average of praxis-431": {"val": {"NO2": {"cnc": 24}, "NO": {"cnc": 67.54666667}}},
"Average of ref": {"NOCNC1 (Processed)": 1.606666667, "NO2CNC1 (Processed)": 6.473333333},
"15 minute \"real\" data": 5.92, "rec": "2019-02-08T00:00:00Z"}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2019-02-07T22:00:00Z", "Average of praxis-431": {"val": {"NO2": {"cnc": 24}, "NO": {"cnc": 67.54666667}}},
"Average of ref": {"NOCNC1 (Processed)": 1.606666667, "NO2CNC1 (Processed)": 6.473333333},
"15 minute \"real\" data": 5.92}

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
https://github.com/south-coast-science/scs_dev/wiki/3:-Data-formats
https://docs.microsoft.com/en-us/dotnet/api/system.datetime.tooadate?view=netframework-4.8
"""

import sys

from scs_analysis.cmd.cmd_sample_iso_8601 import CmdSampleISO8601

from scs_core.data.datetime import DateParser, LocalizedDatetime
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.location.timezone import Timezone


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    parser = None
    timezone = None
    zone = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleISO8601()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if not cmd.zones and not cmd.oad and not DateParser.is_valid_format(cmd.format):
        print("sample_iso_8601: unsupported format: %s" % cmd.format, file=sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_iso_8601: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # format...
        if cmd.format:
            parser = DateParser.construct(cmd.format)

            if cmd.verbose:
                print("sample_iso_8601: %s" % parser, file=sys.stderr)
                sys.stderr.flush()

        # timezone...
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

            document_count += 1

            paths = datum.paths()

            if cmd.oad:
                # OAD...
                if cmd.datetime_path not in paths:
                    print("sample_iso_8601: datetime path '%s' not in %s" % (cmd.datetime_path, jstr), file=sys.stderr)
                    exit(1)

                # ISO 8601...
                iso = LocalizedDatetime.construct_from_oad(datum.node(cmd.datetime_path), tz=zone)

            elif cmd.uses_datetime():
                # datetime...
                if cmd.datetime_path not in paths:
                    print("sample_iso_8601: datetime path '%s' not in %s" % (cmd.datetime_path, jstr), file=sys.stderr)
                    exit(1)

                pieces = datum.node(cmd.datetime_path).rsplit(' ', 1)           # split on last space character

                if len(pieces) != 2:
                    print("sample_iso_8601: malformed datetime '%s' in %s" % (cmd.datetime_path, jstr), file=sys.stderr)
                    exit(1)

                date = pieces[0].strip()
                time = pieces[1].strip()

                # ISO 8601...
                iso = LocalizedDatetime.construct_from_date_time(parser, date, time, tz=zone)

            else:
                # date / time...
                if cmd.date_path not in paths:
                    print("sample_iso_8601: date path '%s' not in %s" % (cmd.date_path, jstr), file=sys.stderr)
                    exit(1)

                if cmd.time_path not in paths:
                    print("sample_iso_8601: time path '%s' not in %s" % (cmd.time_path, jstr), file=sys.stderr)
                    exit(1)

                date = datum.node(cmd.date_path)
                time = datum.node(cmd.time_path)

                # ISO 8601...
                iso = LocalizedDatetime.construct_from_date_time(parser, date, time, tz=zone)

            if iso is None:
                print("sample_iso_8601: malformed date/time in %s" % jstr, file=sys.stderr)
                exit(1)

            if cmd.timezone is not None and cmd.utc:
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

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyError as ex:
        print("sample_iso_8601: KeyError: %s" % ex, file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_iso_8601: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_iso_8601: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
