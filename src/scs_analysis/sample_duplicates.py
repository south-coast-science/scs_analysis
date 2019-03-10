#!/usr/bin/env python3

"""
Created on 3 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_duplicates utility is used to find duplicate values in a sequence of input JSON documents, for a specified
leaf node path. It is particularly useful in searching for duplicate recording datetimes.

If an input document does not contain the specified path, then it is ignored.

The default output report is sequence of JSON dictionaries with a field for each value where duplicates were found.
The value for this field is itself a dictionary, with a field for the index of each input document, and value being
the input document itself.

In the --counts mode, the output report is sequence of JSON dictionaries with a field for each value where duplicates
were found, whose value is the number of matching documents.

SYNOPSIS
sample_duplicates.py [-c] [-v] PATH

EXAMPLES
csv_reader.py climate.csv | sample_duplicates.py -v val.hmd

DOCUMENT EXAMPLE - OUTPUT
default mode:
{"17.5": {"278728": {"val": {"hmd": 17.5, "tmp": 25.7}, "rec": "2019-02-25T15:28:18Z", "tag": "scs-bgx-303"},
"278731": {"val": {"hmd": 17.5, "tmp": 25.7}, "rec": "2019-02-25T15:31:18Z", "tag": "scs-bgx-303"}}}

counts mode:
{"17.5": 2}
"""

import sys

from scs_analysis.cmd.cmd_sample_duplicates import CmdSampleDuplicates

from scs_core.data.duplicates import Duplicates
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


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

    if cmd.verbose:
        print("sample_duplicates: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        dupes = Duplicates()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            if not datum.has_path(cmd.path):
                continue

            dupes.test(document_count, datum.node(cmd.path), datum)

            processed_count += 1


        # ------------------------------------------------------------------------------------------------------------
        # report...

        if cmd.counts:
            for count in dupes.match_counts():
                print(JSONify.dumps(count))

        else:
            for match in dupes.matches():
                print(JSONify.dumps(match))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_duplicates: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_duplicates: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)

            if dupes is not None:
                print("sample_duplicates: values with duplicates: %d" % dupes.matched_key_count, file=sys.stderr)
