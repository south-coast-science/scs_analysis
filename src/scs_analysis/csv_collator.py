#!/usr/bin/env python3

"""
Created on 20 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The csv_collator utility is used to separate the input JSON documents according to the upper and lower bounds of a
sequence of bins. For each bin, assignment follows the rule:

lower bound <= value < upper bound

The upper and lower bounds for the data set should be specified, along with a step size. The number of bins required
to service this domain is calculated automatically. The path identifying the leaf node in the input document where the
value is to be found must be specified.

File names (and sub-directories) as specified by the --file-prefix flag.

Documents that do not contain a field at the specified path, or have values that cannot be evaluated as a float, are
ignored. Likewise, values outside the upper and lower bounds are ignored.

On completion, a summary of the bin assignments is written to stdout.  If no file prefix is given, then the CSV files
are not generated, but the report is still produced.

Two collators are provided in this package: csv_collator collates into separate CSV files (collate to rows),
whereas sample_collator collates into separate columns (collate to columns).

SYNOPSIS
csv_collator.py -l LOWER_BOUND -u UPPER_BOUND -d DELTA [-f FILE_PREFIX] [-v] PATH

EXAMPLES
csv_reader.py alphasense_303_2018-08.csv | \
csv_collator.py -l 5.0 -u 21.0 -d 1.0 -f collation/alphasense_303_2018-08 -v val.sht.hmd.aH

FILES
Output file names are of the form:
FILE-PREFIX_DOMAIN-LOW_DOMAIN-HIGH.csv

SEE ALSO
scs_analysis/csv_collation_summary
scs_analysis/csv_segmentor
scs_analysis/sample_collator

"""

import sys

from scs_analysis.cmd.cmd_csv_collator import CmdCSVCollator
from scs_analysis.handler.csv_collator import CSVCollator

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    collator = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdCSVCollator()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("csv_collator: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        collator = CSVCollator.construct(cmd.lower, cmd.upper, cmd.delta, cmd.file_prefix)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # receive...
        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                break

            document_count += 1

            if cmd.path not in datum.paths():
                continue

            try:
                value = float(datum.node(cmd.path))
            except (TypeError, ValueError):
                continue

            if not collator.collate(value, line):
                continue

            processed_count += 1

        # report...
        for b in collator.bins:
            print(JSONify.dumps(b))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        print("csv_collator: %s" % repr(ex), file=sys.stderr)
        exit(1)

    finally:
        if collator is not None:
            collator.close()

        if cmd.verbose:
            print("csv_collator: documents: %d processed: %d" % (document_count, processed_count),
                  file=sys.stderr)
