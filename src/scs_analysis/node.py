#!/usr/bin/env python3

"""
Created on 11 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The node utility is used to extract a node from within a JSON document. Data is presented as a sequence of documents on
stdin, and the extracted node is passed to stdout. The extracted node may be a leaf node or an internal node. If no
node path is specified, the whole input document is passed to stdout.

The node utility may be set to either ignore documents that do not contain the specified node, or to terminate if the
node is not present.

If the node is an array or other iterable type, then it may be output as a sequence (a list of items separated by
newline characters) according to the -s flag.

SYNOPSIS
node.py [-i] [-s] [-v] [PATH]

EXAMPLES
gases_sampler.py -i10 | node.py val

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:50:27.641+00:00", "val": {"hmd": 59.6, "tmp": 23.8}}

DOCUMENT EXAMPLE - OUTPUT
{"hmd": 59.6, "tmp": 23.8}
"""

import sys

from scs_analysis.cmd.cmd_node import CmdNode

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdNode()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("node: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.array:
            print('[', end='')

        first = True

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            if cmd.ignore and not datum.has_path(cmd.path):
                continue

            node = datum.node(cmd.path)
            document = JSONify.dumps(node)

            if cmd.sequence:
                try:
                    for item in node:
                        print(JSONify.dumps(item))
                except TypeError:
                    print(document)

            else:
                if cmd.array:
                    if first:
                        print(document, end='')
                        first = False

                    else:
                        print(", %s" % document, end='')

                else:
                    print(document)

            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("node: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.array:
            print(']')

