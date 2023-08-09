#!/usr/bin/env python3

"""
Created on 8 Aug 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_localize utility is used to shift the rec datetime field of each input document from its current offset to
the offset determined by the given timezone.

When the transform is applied, the the date / time is shifted, and the UTC offset field is altered accordingly. Thus,
the resulting localised datetime represents the same point in global history, presented for a alternative UTC offset.

In most cases, the UTC offset of a timezone is dependent on daylight saving time. The sample_localize utility is
sensitive to this - the adjustment to the UTC offset of each document's rec field is dependent on its specific
date / time value. Thus, UTC offsets are not the same thing as timezones! It is always safe to shift from UTC to a
timezone, but sifting to a subsequent timezone can have unexpected results, particularly on daylight saving time
boundaries.

The sample_localize utility halts on input lines which have no datetime field, or a datetime field with a
malformed ISO 8601 datetime.

Note that the timezone of a South Coast Science device is normally reported on its status topic.

SYNOPSIS
sample_localize.py { -z | -t TIMEZONE_NAME [-i ISO_PATH] [-v]

EXAMPLES
aws_topic_history.py -s 2023-03-26T00:50:00Z -e 2023-03-26T01:10:00Z \
south-coast-science-demo/brighton-urban/loc/1/climate | \
sample_localize.py -v -t Europe/London

DOCUMENT EXAMPLE - INPUT
{"val": {"hmd": 73.6, "tmp": 12.0, "bar": {"pA": 99.272}}, "rec": "2023-03-26T01:00:09Z",
"ver": 1.0, "tag": "scs-bgx-570"}

DOCUMENT EXAMPLE - OUTPUT
{"val": {"hmd": 73.6, "tmp": 12.0, "bar": {"pA": 99.272}}, "rec": "2023-03-26T02:00:09+01:00",
"ver": 1.0, "tag": "scs-bgx-570"}

SEE ALSO
scs_analysis/sample_iso_8601
scs_analysis/sample_time_shift

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
https://github.com/south-coast-science/scs_dev/wiki/3:-Data-formats
http://pytz.sourceforge.net
"""

import sys

from scs_analysis.cmd.cmd_sample_localize import CmdSampleLocalize

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.location.timezone import Timezone

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleLocalize()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_localize', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # helper...

        if cmd.zones:
            for zone in Timezone.zones():
                print(zone, file=sys.stderr)
            exit(0)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        if not Timezone.is_valid(cmd.timezone):
            logger.error("unrecognised timezone: '%s'." % cmd.timezone)
            exit(2)

        timezone = Timezone(cmd.timezone)
        zone = timezone.zone


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            try:
                iso_node = datum.node(cmd.iso)
            except KeyError:
                logger.error("ISO path '%s' not in %s" % (cmd.iso, jstr))
                exit(1)

            iso = LocalizedDatetime.construct_from_iso8601(iso_node)

            if iso is None:
                logger.error("malformed datetime '%s' in %s" % (iso_node, jstr))
                exit(1)

            datum.append(cmd.iso, iso.localize(zone).as_iso8601())

            # report...
            print(JSONify.dumps(datum))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        if not cmd.zones:
            logger.info("documents: %d processed: %d" % (document_count, processed_count))
