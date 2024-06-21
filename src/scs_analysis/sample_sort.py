#!/usr/bin/env python3

"""
Created on 19 Sep 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_sort utility is used to sort the JSON documents provided on stdin, according to one or more fields indicated
by the given paths. It is up to the user to ensure that each document contains a leaf node for each path, and that the
type of each node is compatible (i.e. all values for a given path are numeric or are strings).

WARNING: no support is given for localised datetimes. Therefore, for example, 2022-09-16T09:00:00Z is considered
not equal to 2022-09-16T10:00:00+01:00.

SYNOPSIS
sample_sort.py [-r] [-v] SORT_PATH_1 [...SORT_PATH_N]

EXAMPLES
csv_reader.py -v ref-scs-bgx-508-20H1-slp16-vcal-err-clean-on-train-vE-exg.csv | \
sample_sort.py -v rec | \
csv_writer.py -v ref-scs-bgx-508-20H1-slp16-vcal-err-clean-on-train-vE-exg-sorted.csv
"""

import sys

from scs_analysis.cmd.cmd_sample_sort import CmdSampleSort

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleSort()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_sort', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        data = []

        # ingest...
        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line, sort_paths=cmd.sort_paths)

            if datum is None:
                continue

            document_count += 1

            data.append(datum)

        # report...
        for datum in sorted(data, reverse=cmd.reverse):
            print(JSONify.dumps(datum))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except (KeyError, TypeError) as ex:
        logger.error(repr(ex))
        exit(1)

    finally:
        logger.info("documents: %d" % document_count)
