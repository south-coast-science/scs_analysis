#!/usr/bin/env python3

"""
Created on 24 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_analysis/socket_receiver.py | ./scs_analysis/sample_conv.py val.afe.sns.CO -s 0.321
"""

import sys

from scs_analysis.cmd.cmd_sample_filter import CmdSampleFilter

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.sys.exception_report import ExceptionReport


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleFilter()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        max_datum = None

        for line in sys.stdin:
            sample_datum = PathDict.construct_from_jstr(line)

            if max_datum is None or sample_datum.node(cmd.path) > max_datum.node(cmd.path):
                max_datum = sample_datum

        if max_datum:
            print(JSONify.dumps(max_datum.node()))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("sample_max: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
