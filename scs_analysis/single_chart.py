#!/usr/bin/env python3

'''
Created on 21 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./socket_receiver.py | ./single_chart.py -r val.afe.sns.CO.cnc
'''

import sys
import warnings

from scs_analysis.chart.single_chart import SingleChart
from scs_analysis.cmd.cmd_single_chart import CmdSingleChart

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    warnings.filterwarnings("ignore", module="matplotlib")

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSingleChart()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    scope = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        scope = SingleChart(cmd.batch_mode, cmd.x, cmd.y[0], cmd.y[1], cmd.relative, cmd.path)

        if cmd.verbose:
            print(scope, file=sys.stderr)


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
            print("single_chart: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print("single_chart: " + type(ex).__name__, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        if cmd.verbose:
            print(scope, file=sys.stderr)
            print("single_chart: holding", file=sys.stderr)

        if scope is not None:
            try:
                scope.hold()
            except:
                pass
