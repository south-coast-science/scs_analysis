#!/usr/bin/env python3

"""
Created on 3 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_time_shift utility is used to add a unit of time to the reported datetime of each record in the input
data set. This is useful when reference data is labelled for the beginning of the time period instead of the end
(the latter is the form used by South Coast Science).

The path to the ISO 8601 recording datetime may be given, otherwise it defaults to 'rec'.

SYNOPSIS
sample_time_shift.py -t { + | - } [[DD-]HH:]MM[:SS] [-v] [PATH]

EXAMPLES
csv_reader.py -v mfidikwe.csv | sample_time_shift.py -v -t + 00:01:00 | csv_writer.py -v mfidikwe_shifted.csv

DOCUMENT EXAMPLE - INPUT
{"rec": "2021-10-31T22:00:00Z", "meteo": {"T": 15.2, "rH": 62}, "gas": {"SO2": 11}}
...

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2021-10-31T22:01:00Z", "meteo": {"T": 15.2, "rH": 62}, "gas": {"SO2": 11}}
...

SEE ALSO
scs_analysis/sample_iso_8601
scs_analysis/sample_localize
"""

import sys

from scs_analysis.cmd.cmd_sample_time_shift import CmdSampleTimeShift

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleTimeShift()

    Logging.config('sample_time_shift', verbose=cmd.verbose)
    logger = Logging.getLogger()

    if not cmd.is_valid_timedelta():
        logger.error("invalid format for timedelta.")
        exit(2)

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                break

            document_count += 1

            rec = LocalizedDatetime.construct_from_iso8601(datum.node(cmd.path))
            shifted = rec + cmd.timedelta if cmd.positive else rec - cmd.timedelta

            datum.append(cmd.path, shifted.as_iso8601())

            print(JSONify.dumps(datum))
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
        logger.info("documents: %d processed: %d" % (document_count, processed_count))
