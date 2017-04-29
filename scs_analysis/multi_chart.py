#!/usr/bin/env python3

"""
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./socket_receiver.py | ./multi_chart.py val.opc.pm10 val.opc.pm2p5 val.opc.pm1 -x 120 -e
"""

import tkinter
import sys
import warnings

from scs_analysis.chart.multi_chart import MultiChart
from scs_analysis.cmd.cmd_multi_chart import CmdMultiChart

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.sys.exception_report import ExceptionReport


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    warnings.filterwarnings("ignore", module="matplotlib")

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMultiChart()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    scope = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        scope = MultiChart(cmd.batch_mode, cmd.x, cmd.y[0], cmd.y[1], *cmd.paths)

        if cmd.verbose:
            print(scope, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                break

            if cmd.echo:
                print(JSONify.dumps(datum.node()))
                sys.stdout.flush()

            scope.plot(datum)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("multi_chart: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        if cmd.verbose:
            print(scope, file=sys.stderr)
            print("multi_chart: holding", file=sys.stderr)

        if scope is not None:
            try:
                scope.hold()

            except tkinter.TclError:
                pass
