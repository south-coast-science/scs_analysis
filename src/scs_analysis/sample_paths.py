#!/usr/bin/env python3

"""
Created on 18 Sep 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_exegesis

DESCRIPTION
The sample_paths utility is used to

Typically use with csv_reader --limit=1 flag.

SYNOPSIS
sample_paths.py [-v]

EXAMPLES
csv_reader.py -v -l 1 ref-scs-opc-116-gases-2021H1-vcal-slp-err-vE-exg.csv | sample_paths.py
"""

import sys

from scs_analysis.cmd.cmd_sample_paths import CmdSamplePaths

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    paths = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSamplePaths()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_paths', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            if paths:
                continue

            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            paths = datum.paths()


        # report...
        print(JSONify.dumps(paths))
        sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)
