#!/usr/bin/env python3

"""
Created on 24 Oct 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_aggregate utility is used to

SYNOPSIS
sample_aggregate.py [-v] [PATH]

EXAMPLES
sample_aggregate.py
"""

import sys

from scs_analysis.cmd.cmd_sample_record import CmdSampleRecord

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleRecord()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_min: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        min_datum = None

        for line in sys.stdin:
            sample_datum = PathDict.construct_from_jstr(line)

            if min_datum is None or sample_datum.node(cmd.path) < min_datum.node(cmd.path):
                min_datum = sample_datum

        if min_datum:
            print(JSONify.dumps(min_datum.node()))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_aggregate: KeyboardInterrupt", file=sys.stderr)
