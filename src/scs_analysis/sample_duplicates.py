#!/usr/bin/env python3

"""
Created on 3 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_duplicates utility is used to find duplicate values in a sequence of input JSON documents, optionally
for a specified node path. It is particularly useful in searching for duplicate recording datetimes.

If an input document does not contain the specified path, then it is ignored.

In the default mode, the utility outputs the rows that were duplicates (or contained duplicate field values). If the
--exclude flag is set, then sample_duplicates generates a version of the input data that contains no duplicates.

In the --counts mode, the output report is sequence of JSON dictionaries with a field for each value where duplicates
were found, whose value is the number of matching documents.

SYNOPSIS
sample_duplicates.py [{ -x | -c }] [-v] [PATH]

EXAMPLES
csv_reader.py climate.csv | sample_duplicates.py -v val.hmd

DOCUMENT EXAMPLE - OUTPUT
default mode:
{"val": {"hmd": 17.5, "tmp": 25.7}, "rec": "2019-02-25T15:28:18Z", "tag": "scs-bgx-303"}
{"val": {"hmd": 17.5, "tmp": 25.7}, "rec": "2019-02-25T15:31:18Z", "tag": "scs-bgx-303"}

counts mode:
{"17.5": 2}
"""

import sys

from scs_analysis.cmd.cmd_sample_duplicates import CmdSampleDuplicates

from scs_core.data.duplicates import Duplicates
from scs_core.data.path_dict import PathDict

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    dupes = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleDuplicates()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_duplicates', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        dupes = Duplicates()
        non_dupes = []

        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            if not datum.has_sub_path(cmd.path):
                continue

            is_duplicate = dupes.test(document_count, datum.node(cmd.path), datum)

            if not cmd.counts:
                if cmd.exclude:
                    if not is_duplicate:
                        non_dupes.append(jstr)
                else:
                    if is_duplicate:
                        print(jstr)

            processed_count += 1


        # ------------------------------------------------------------------------------------------------------------
        # report...

        if cmd.exclude:
            for datum in non_dupes:
                print(datum)

        if cmd.counts:
            for count in dupes.match_counts():
                print(count)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        logger.info("documents: %d processed: %d" % (document_count, processed_count))
        logger.info("values with duplicates: %d total duplicates: %d" % (dupes.matched_key_count, dupes.total_matches))
