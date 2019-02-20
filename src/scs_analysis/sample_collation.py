#!/usr/bin/env python3

"""
Created on 11 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_airwatch utility is used to

SYNOPSIS
sample_airwatch.py { -z | TIMEZONE_NAME }

EXAMPLES
aws_topic_history.py south-coast-science-dev/production-test/loc/1/climate -s 2018-10-28T00:00:00+00:00 \
-e 2018-10-28T03:00:00+00:00 | sample_airwatch.py -n Europe/Paris

DOCUMENT EXAMPLE - INPUT
{"val": {"hmd": 49.7, "tmp": 17.5}, "rec": "2018-10-28T00:00:46.037+00:00", "tag": "scs-be2-2"}

DOCUMENT EXAMPLE - OUTPUT
{"val": {"hmd": 49.7, "tmp": 17.5}, "rec": "2018-10-28T01:00:46.037+01:00", "tag": "scs-be2-2"}

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
http://pytz.sourceforge.net
"""

import json
import sys

from collections import OrderedDict

from scs_analysis.cmd.cmd_sample_collation import CmdSampleCollation

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.climate.absolute_humidity import AbsoluteHumidity

from scs_core.location.timezone import Timezone


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    timezone = None
    zone = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleCollation()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_collation: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        bins = []

        lower = cmd.lower

        while True:
            upper = round(lower + cmd.step, 1)
            bins.append((lower, upper))
            lower = upper

            if lower >= cmd.upper:
                break

        print("len: %d bins: %s" % (len(bins), bins))


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # for line in sys.stdin:
        #     datum = PathDict.construct_from_jstr(line)
        #
        #     if datum is None:
        #         break
        #
        #     target = PathDict()
        #
        #     ah = datum.node(path)
        #
        #     if lower_bound <= ah < upper_bound:
        #         report...
        #         print(JSONify.dumps(datum.node()))
        #         sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_collation: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_collation: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
