#!/usr/bin/env python3

"""
Created on 12 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The node_shift utility is used to time-shift JSON document nodes or sub-nodes representing timeline data.

A sequence of documents is accepted from stdin. If a positive offset on N is specified, then the content of the
specified source node is postponed by N documents. Output values are therefore aligned with a datetime that is in the
future, relative to their original position. If a negative offset is specified, then values are shifted to the past.

Some output documents inevitably have null values: in the case of positive shift operations, the initial documents have
null values, in the case of negative offsets, the final documents have null values. These documents can be
included in the output (preserving the input document count) if the --fill flag is specified. Otherwise, these
documents are discarded.

If TARGET_SUB_PATH is specified, then the shifted node will be renamed.

SYNOPSIS
node_shift.py -o OFFSET [-r] [-v] SOURCE_SUB_PATH [TARGET_SUB_PATH]

EXAMPLES
csv_reader.py climate.csv | node_shift.py -v -o 1 -f val.hmd val.hmd-shift-1 | csv_writer.py climate-shifted.csv
"""

import sys

from scs_analysis.cmd.cmd_node_shift import CmdNodeShift

from scs_core.data.json import JSONify
from scs_core.data.node_shifter import NodeShifter
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    output_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdNodeShift()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("node_shift: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        shifter = NodeShifter(cmd.offset, cmd.fill, cmd.source_path, cmd.target_path)

        if cmd.verbose:
            print("node_shift: %s" % shifter, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # input...
        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            if not datum.has_sub_path(cmd.source_path):
                print("node_shift: source path '%s' not in %s" % (cmd.source_path, jstr),
                      file=sys.stderr)
                exit(1)

            try:
                target = shifter.shift(datum)

            except TypeError:
                target = None
                print("node_shift: incompatible types for '%s' and '%s'" % (cmd.source_path, cmd.target_path),
                      file=sys.stderr)
                exit(1)

            if target is None:
                continue

            # report...
            print(JSONify.dumps(target))
            sys.stdout.flush()

            output_count += 1

        # residual...
        while True:
            target = shifter.pop()

            if target is None:
                break

            print(JSONify.dumps(target))
            sys.stdout.flush()

            output_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("node_shift: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("node_shift: documents: %d output: %d" % (document_count, output_count), file=sys.stderr)
