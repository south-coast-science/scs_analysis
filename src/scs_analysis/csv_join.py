#!/usr/bin/env python3

"""
Created on 22 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The csv_join utility performs an SQL join operation on a pair of CSV files. This is particularly useful where a
comparison is to be made on timeline data from two devices.

All four join types are supported: inner, left outer, right outer and full outer. Inner joins are used when the output
should only contain rows that match on their primary key.

Output is in the form of a sequence of JSON documents containing three fields: rec, left table contents (labelled for
the left PREFIX) and right table contents (labelled for the right PREFIX). The left and right contents do not contain
their primary key fields. For outer joins, content nodes may be null.

The --iso8601 flag is provided to indicate that the primary key should be interpreted as a ISO 8601 datetime. This is
useful where data sets use alternate datetime formats such as 2019-02-22T01:00:00Z and 2019-02-22T01:00:00+00:00.

If the --verbose flag is used, a summary of the join operation is written to stderr.

SYNOPSIS
csv_join.py [-t TYPE] -l PREFIX PK FILENAME -r PREFIX PK FILENAME [-i] [-v]

EXAMPLES
csv_join.py -i -v -l praxis rec praxis_301/praxis_301_2018-08.csv -r ref rec ref/ref_2018-08.csv

DOCUMENT EXAMPLE - INPUT
left:
{"rec": "2019-02-01T02:00:00Z", "val": {"NO2": {"weV": 0.297185, "cnc": 40.8, "aeV": 0.298467, "weC": 0.002271}}}

right:
{"rec": "2019-02-01T02:00:00Z", "val": {"NO2": {"status": "P", "units": "ugm-3", "dns": 34.0}}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2019-02-01T02:00:00Z", "praxis": {"val": {"NO2": {"weV": 0.297185, "cnc": 40.8, "aeV": 0.298467,
"weC": 0.002271}}}, "ref": {"val": {"NO2": {"status": "P", "units": "ugm-3", "dns": 34.0}}}}

SEE ALSO
scs_analysis/csv_reader

RESOURCES
https://www.w3schools.com/sql/sql_join.asp
"""

import sys

from scs_analysis.cmd.cmd_csv_join import CmdCSVJoin

from scs_core.csv.csv_reader import CSVReader

from scs_core.data.join import Join
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    reader = None
    result = None

    left_document_count = 0
    left_processed_count = 0

    right_document_count = 0
    right_processed_count = 0

    joined_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdCSVJoin()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if not Join.is_valid_type(cmd.type):
        print("csv_join: invalid join type: %s" % cmd.type, file=sys.stderr)
        exit(2)

    if cmd.verbose:
        print("csv_join: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        join = Join.construct(cmd.left_prefix, cmd.left_pk, cmd.right_prefix, cmd.right_pk, cmd.iso8601)

        try:
            reader = CSVReader(filename=cmd.left_filename)
        except FileNotFoundError:
            print("csv_join: file not found: %s" % cmd.left_filename, file=sys.stderr)
            exit(1)

        for row in reader.rows:
            jstr = row.strip()
            datum = PathDict.construct_from_jstr(row)

            if datum is None:
                continue

            left_document_count += 1

            if cmd.left_pk not in datum.paths():
                print("csv_join: pk '%s' missing: %s" % (cmd.left_pk, jstr), file=sys.stderr)
                exit(1)

            if datum.node(cmd.left_pk) == '':
                continue

            try:
                join.append_to_left(datum)
            except ValueError as ex:
                print("csv_join: invalid pk '%s' in: %s" % (datum.node(cmd.left_pk), jstr), file=sys.stderr)
                exit(1)

            left_processed_count += 1

        reader.close()

        try:
            reader = CSVReader(filename=cmd.right_filename)
        except FileNotFoundError:
            print("csv_join: file not found: %s" % cmd.right_filename, file=sys.stderr)
            exit(1)

        for row in reader.rows:
            jstr = row.strip()
            datum = PathDict.construct_from_jstr(row)

            if datum is None:
                continue

            right_document_count += 1

            if cmd.right_pk not in datum.paths():
                print("csv_join: pk '%s' missing: %s" % (cmd.right_pk, jstr), file=sys.stderr)
                exit(1)

            if datum.node(cmd.right_pk) == '':
                continue

            try:
                join.append_to_right(datum)
            except ValueError as ex:
                print("csv_join: invalid pk '%s' in: %s" % (datum.node(cmd.right_pk), jstr), file=sys.stderr)
                exit(1)

            right_processed_count += 1

        reader.close()

        if cmd.verbose:
            print("csv_join: %s" % join, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.type == 'LEFT':
            operation = join.left

        elif cmd.type == 'RIGHT':
            operation = join.right

        elif cmd.type == 'FULL':
            operation = join.full

        else:
            operation = join.inner

        for datum in operation():
            print(JSONify.dumps(datum))
            sys.stdout.flush()

            joined_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd and cmd.verbose:
            print("csv_join: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("csv_join: left: documents: %d processed: %d" % (left_document_count, left_processed_count),
                  file=sys.stderr)
            print("csv_join: right: documents: %d processed: %d" % (right_document_count, right_processed_count),
                  file=sys.stderr)
            print("csv_join: joined: %d" % joined_count,
                  file=sys.stderr)
