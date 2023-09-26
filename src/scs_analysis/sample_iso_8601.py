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

The --no-time flag should be used where the input document contains a date but no time indicator. In this case, the
the data is interpreted as being an aggregate of the whole date period. For example, if the input date is 31/01/2022
then the output datetime will be 2022-02-01T00:00:00 (the date is moved on by one day because the datetime field
indicates the end of the sample period).

If the input datetimes are not UTC, then the timezone of the input data should be specified. In this case, the
datetime may optionally be shifted to UTC.

All fields in the input document are presented in the output document, with the exception of the selected date, time or
datetime fields. The default name for the ISO 8601 datetime output field is 'rec' but an alternate name may be
specified.

SYNOPSIS
sample_iso_8601.py { -z | { -o | -f DATE_FORMAT } [-t TIMEZONE_NAME [-u]] [-i ISO_PATH]
{ DATETIME_PATH [-n] | DATE_PATH TIME_PATH } } [-s] [-v]

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

SEE ALSO
scs_analysis/sample_localize
scs_analysis/sample_time_shift

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

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    parser = None
    timezone = None
    zone = None
    pieces = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleISO8601()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_iso_8601', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # validation...

        if not cmd.zones and not cmd.oad and not DateParser.is_valid_format(cmd.format):
            logger.error("unsupported format: %s" % cmd.format)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # format...
        if cmd.format:
            parser = DateParser.construct(cmd.format)
            logger.info(parser)

        # timezone...
        if cmd.timezone is not None:
            try:
                timezone = Timezone(cmd.timezone)
                zone = timezone.zone

            except ValueError:
                logger.error("unrecognised timezone: '%s'." % cmd.timezone)
                exit(2)

            logger.info(timezone)


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
                    logger.error("datetime path '%s' not in %s" % (cmd.datetime_path, jstr))
                    exit(1)

                # ISO 8601...
                iso = LocalizedDatetime.construct_from_oad(datum.node(cmd.datetime_path), tz=zone)

            elif cmd.uses_datetime():
                # datetime...
                if cmd.datetime_path not in paths:
                    logger.error("datetime path '%s' not in %s" % (cmd.datetime_path, jstr))
                    exit(1)

                try:
                    pieces = datum.node(cmd.datetime_path).rsplit(' ', 1)           # split on last space character

                except AttributeError:
                    if cmd.skip_malformed:
                        continue

                    logger.error("malformed datetime (AttributeError) '%s' in %s" % (cmd.datetime_path, jstr))
                    exit(1)

                if (cmd.no_time and len(pieces) != 1) or (not cmd.no_time and len(pieces) != 2):
                    if cmd.skip_malformed:
                        continue

                    logger.error("malformed datetime (field count) '%s' in %s" % (cmd.datetime_path, jstr))
                    exit(1)

                date = pieces[0].strip()
                time = '24:00:00' if cmd.no_time else pieces[1].strip()

                # ISO 8601...
                iso = LocalizedDatetime.construct_from_date_time(parser, date, time, tz=zone)

            else:
                # date / time...
                if cmd.date_path not in paths:
                    logger.error("date path '%s' not in %s" % (cmd.date_path, jstr))
                    exit(1)

                if cmd.time_path not in paths:
                    logger.error("time path '%s' not in %s" % (cmd.time_path, jstr))
                    exit(1)

                date = datum.node(cmd.date_path)
                time = datum.node(cmd.time_path)

                # ISO 8601...
                iso = LocalizedDatetime.construct_from_date_time(parser, date, time, tz=zone)

            if iso is None:
                if cmd.skip_malformed:
                    continue

                logger.error("malformed date/time in %s" % jstr)
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

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        logger.error(repr(ex))
        exit(1)

    finally:
        if not cmd.zones:
            logger.info("documents: %d processed: %d" % (document_count, processed_count))
