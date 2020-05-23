#!/usr/bin/env python3

"""
Created on 10 Mar 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The csv_segmentor utility is used to segment the input stream of JSON documents into CSV files whose rows
have contiguous datetime values.

Contiguity is defined by the --max-interval flag. If the time interval between a document and the previous document is
greater than this interval, then the current CSV file is closed, and a new file is opened. File names (and
sub-directories) as specified by the --file-prefix flag. The datetime of the first row of CSV file is appended to the
prefix.

The input documents must contain a field carrying an ISO 8601 datetime. If the field in a given document is empty or
malformed, the document is ignored. If the field is not present in any document, the csv_segmentor utility
terminates.

The csv_segmentor utility generates a report giving the specifications of each contiguous block. If no file prefix
is given, then the CSV files are not generated, but the report is still produced.

SYNOPSIS
csv_segmentor.py -m { [[DD-]HH:]MM[:SS] | :SS } [-i ISO] [-f FILE_PREFIX] [-v]

EXAMPLES
csv_reader.py -v scs-bgx-508-gases-2020-Q1.csv | \
csv_segmentor.py -m 06:00 -f segments/scs-bgx-508-gases-2020-Q1 -v | \
csv_writer.py -v segments/scs-bgx-508-gases-2020-Q1-report.csv

FILES
Output file names are of the form:
FILE-PREFIX_BLOCK_START_DATETIME.csv

DOCUMENT EXAMPLE - OUTPUT
{"start": "2019-01-01T00:00:01Z", "end": "2019-01-04T10:04:51Z", "prev-interval": "",
"max-interval": "00-00:00:11", "count": 29550}
{"start": "2019-01-04T10:29:21Z", "end": "2019-01-04T10:37:41Z", "prev-interval": "00-00:24:30",
"max-interval": "00-00:00:10", "count": 51}
{"start": "2019-01-04T11:35:49Z", "end": "2019-01-04T11:41:19Z", "prev-interval": "00-00:58:07",
"max-interval": "00-00:00:10", "count": 34}

SEE ALSO
scs_analysis/csv_collator
"""

import sys

from scs_analysis.cmd.cmd_csv_segmentor import CmdCSVSegmentor
from scs_analysis.handler.csv_segmentor import CSVSegmentor

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    segmentor = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdCSVSegmentor()

    if not cmd.is_valid_interval():
        print("csv_segmentor: invalid format for max interval.", file=sys.stderr)
        exit(2)

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("csv_segmentor: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        segmentor = CSVSegmentor(cmd.max_interval.delta, cmd.file_prefix)

        if cmd.verbose:
            print("csv_segmentor: %s" % segmentor, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # receive...
        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                break

            document_count += 1

            if cmd.iso not in datum.paths():
                raise KeyError(cmd.iso)

            rec = LocalizedDatetime.construct_from_iso8601(datum.node(cmd.iso))

            if rec is None:
                continue

            segmentor.collate(rec, line)

            processed_count += 1

        # report...
        for block in segmentor.blocks:
            print(JSONify.dumps(block))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyError as ex:
        print("csv_segmentor: KeyError: %s" % ex, file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("csv_segmentor: KeyboardInterrupt", file=sys.stderr)

    finally:
        if segmentor is not None:
            segmentor.close()

        if cmd.verbose:
            print("csv_segmentor: documents: %d processed: %d segments: %d" %
                  (document_count, processed_count, len(segmentor)), file=sys.stderr)
