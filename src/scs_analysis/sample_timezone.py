#!/usr/bin/env python3

"""
Created on 19 Nov 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_timezone utility is used to shift the rec datetime field of each input document from its current offset to
the offset determined by the given timezone. This is particularly useful when using data visualisation systems that are
not localisation-aware.

When the transform is applied, the the date / time is shifted, and the UTC offset field is altered accordingly. Thus,
the resulting localised datetime represents the same point in global history, presented for a alternative UTC offset.

In most cases, the UTC offset of a timezone is dependent on daylight saving time. The sample_timezone utility is
sensitive to this - the adjustment to the UTC offset of each document's rec field is dependent on its specific
date / time value. Thus, UTC offsets are not the same thing as timezones! It is always safe to shift from UTC to a
timezone, but sifting to a subsequent timezone can have unexpected results, particularly on daylight saving time
boundaries.

The sample_timezone utility silently ignores input lines which have:
* A malformed JSON document
* No 'rec' field, or a 'rec' field with a malformed ISO 8601 datetime

Note that the timezone of a South Coast Science device is normally reported on its status topic.

SYNOPSIS
sample_timezone.py { -z | [-i ISO_PATH] TIMEZONE_NAME }

EXAMPLES
aws_topic_history.py south-coast-science-dev/production-test/loc/1/climate -s 2018-10-28T00:00:00+00:00 \
-e 2018-10-28T03:00:00+00:00 | sample_timezone.py -n Europe/Paris

DOCUMENT EXAMPLE - INPUT
{"val": {"hmd": 49.7, "tmp": 17.5}, "rec": "2018-10-28T00:00:46.037+00:00", "tag": "scs-be2-2"}

DOCUMENT EXAMPLE - OUTPUT
{"val": {"hmd": 49.7, "tmp": 17.5}, "rec": "2018-10-28T01:00:46.037+01:00", "tag": "scs-be2-2"}

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
http://pytz.sourceforge.net

BUGS
Because the sample_timezone utility is based on the pytz library, offset errors may occur when using the Etc/GMT+/-N
pseudo-timezones.
"""

import json
import sys

from scs_analysis.cmd.cmd_sample_timezone import CmdSampleTimezone

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

from scs_core.location.timezone import Timezone


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    timezone = None
    zone = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleTimezone()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_timezone: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if cmd.timezone is not None:
            try:
                timezone = Timezone(cmd.timezone)
                zone = timezone.zone

            except ValueError:
                print("sample_timezone: unrecognised name:%s" % cmd.timezone, file=sys.stderr)
                exit(2)

            if cmd.verbose:
                print("sample_timezone: %s" % timezone, file=sys.stderr)
                sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.zones:
            for zone in Timezone.zones():
                print(zone, file=sys.stderr)
            exit(0)

        for line in sys.stdin:
            try:
                jdict = json.loads(line)
            except ValueError:
                continue

            document_count += 1

            try:
                rec = jdict[cmd.iso]
            except KeyError:
                continue

            # zone shift...
            datetime = LocalizedDatetime.construct_from_iso8601(rec)

            if datetime is None:
                continue

            jdict['rec'] = datetime.localize(zone).as_iso8601()

            # report...
            print(JSONify.dumps(jdict))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_timezone: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_timezone: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
