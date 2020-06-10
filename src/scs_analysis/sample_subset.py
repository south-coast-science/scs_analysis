#!/usr/bin/env python3

"""
Created on 26 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_subset utility is used to find a subset of documents whose value for a specified field lies either
inside or outside one or two bounding values.

Input is in the form of a stream of JSON documents. Documents are written to stdout if they match the specification,
and discarded otherwise. Documents which do not have the specified field, or have an empty field value are also
discarded. If a field value is present but cannot be cast to the correct type, then the sample_subset utility
terminates.

The type of the field may be specified explicitly as either numeric or ISO 8601 datetime. If no specification is given,
the value is interpreted as a string.

Evaluation follows the rule:

lower bound <= value < upper bound

Both upper and lower bounds are optional. If both are present, then the lower bound value must be less than the upper
bound value. If neither are present, then the sample_subset utility filters out documents with missing fields or
empty values.

If the --exclusions flag is used, the sample_subset utility outputs only the documents that do not fit within the
specified bounds. Note that, in this case, documents with missing or empty fields are still discarded.

SYNOPSIS
sample_subset.py [{ -i | -n }] [-l LOWER] [-u UPPER] [-x] [-v] PATH

EXAMPLES
csv_reader.py praxis_303.csv | sample_subset.py -v -i -l 2018-09-26T00:00:00Z -u 2018-09-27T00:00:00Z rec
"""

import sys

from scs_analysis.cmd.cmd_sample_subset import CmdSampleSubset

from scs_core.data.datum import Datum
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    lower_bound = None
    upper_bound = None
    value = None

    document_count = 0
    processed_count = 0
    output_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleSubset()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_subset: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        try:
            lower_bound = cmd.lower
        except ValueError as ex:
            print("sample_subset: invalid value for lower bound: %s" % ex, file=sys.stderr)
            exit(2)

        try:
            upper_bound = cmd.upper
        except ValueError as ex:
            print("sample_subset: invalid value for upper bound: %s" % ex, file=sys.stderr)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # value...
            if cmd.path not in paths:
                continue

            value_node = datum.node(cmd.path)

            if value_node == '':
                continue

            if cmd.iso8601:
                value = Datum.datetime(value_node)

                if value is None:
                    print("sample_subset: invalid ISO 8601 value '%s' in %s" % (value_node, jstr), file=sys.stderr)
                    exit(1)

            elif cmd.numeric:
                value = Datum.float(value_node)

                if value is None:
                    print("sample_subset: invalid numeric value '%s' in %s" % (value_node, jstr), file=sys.stderr)
                    exit(1)

            else:
                value = value_node

                if not value:
                    continue

            processed_count += 1

            # bounds...
            try:
                in_bounds = (lower_bound is None or value >= lower_bound) and \
                            (upper_bound is None or value < upper_bound)
            except TypeError as ex:
                in_bounds = None
                print("sample_subset: TypeError: %s" % jstr, file=sys.stderr)
                exit(1)

            if (cmd.inclusions and not in_bounds) or (cmd.exclusions and in_bounds):
                continue

            # report...
            print(jstr)
            sys.stdout.flush()

            output_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyError as ex:
        print("sample_subset: KeyError: %s" % ex, file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_subset: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_subset: documents: %d processed: %d output: %d" %
                  (document_count, processed_count, output_count), file=sys.stderr)
