#!/usr/bin/env python3

"""
Created on 4 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_reader utility is used to convert data from comma-separated value (CSV) format to JSON format.

The names of columns given in the CSV header row indicate paths into the JSON document: dictionary fields are separated
from their container by a period ('.') character, and JSON array members separated from their container by a
colon (':') character.

The first row of the CSV file (or stdin input) is assumed to be a header row. If there are more columns in the body of
the CSV than in the header, excess values are ignored.

By default, output is in the form of a sequence of JSON documents, separated by newlines. If the array (-a) option is
selected, output is in the form of a JSON array - the output opens with a '[' character, documents are separated by
the ',' character, and the output is terminated by a ']' character.

SYNOPSIS
csv_reader.py [-a] [-v] [FILENAME_1 ... FILENAME_N]

EXAMPLES
csv_reader.py sht.csv

DOCUMENT EXAMPLE - INPUT
tag,rec,val.hmd,val.tmp
scs-ap1-6,2018-04-04T14:50:38.394+00:00,59.7,23.8
scs-ap1-6,2018-04-04T14:55:38.394+00:00,59.8,23.9

DOCUMENT EXAMPLE - OUTPUT
Sequence mode:
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:50:38.394+00:00", "val": {"hmd": 59.7, "tmp": 23.8}}
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:55:38.394+00:00", "val": {"hmd": 59.8, "tmp": 23.9}}

Array mode:
[{"tag": "scs-ap1-6", "rec": "2018-04-04T14:50:38.394+00:00", "val": {"hmd": 59.7, "tmp": 23.8}},
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:55:38.394+00:00", "val": {"hmd": 59.8, "tmp": 23.9}}]

SEE ALSO
scs_analysis/csv_writer
"""

import sys

from scs_analysis.cmd.cmd_csv_reader import CmdCSVReader

from scs_core.csv.csv_reader import CSVReader


# TODO: implement multiple files across the system

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    reader = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdCSVReader()

    if cmd.verbose:
        print("csv_reader: %s" % cmd, file=sys.stderr)

    if cmd.array:
        print('[', end='')

    try:
        for filename in cmd.filenames:

            # --------------------------------------------------------------------------------------------------------
            # resources...

            reader = CSVReader(filename)

            if cmd.verbose:
                print("csv_reader: %s" % reader, file=sys.stderr)
                sys.stderr.flush()


            # --------------------------------------------------------------------------------------------------------
            # run...

            first = True

            for datum in reader.rows:
                if cmd.array:
                    if first:
                        print(datum, end='')
                        first = False

                    else:
                        print(", %s" % datum, end='')

                else:
                    print(datum)

                sys.stdout.flush()

            # close...
            if reader is not None:
                reader.close()

    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd and cmd.verbose:
            print("csv_reader: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.array:
            print(']')
