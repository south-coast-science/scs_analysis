#!/usr/bin/env python3

"""
Created on 3 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./socket_receiver.py | ./sample_conv.py val.afe.sns.CO -s 0.321 | ./sample_error.py val.afe.sns.CO.conv | ./multi_chart.py val.afe.sns.CO.conv.src val.afe.sns.CO.conv.agr -e | ./histo_chart.py val.afe.sns.CO.conv.err -x -10 10 -e -o err.csv
"""

import sys
import warnings

from scs_analysis.chart.histo_chart import HistoChart
from scs_analysis.cmd.cmd_histo import CmdHisto

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.sys.exception_report import ExceptionReport


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    warnings.filterwarnings("ignore", module="matplotlib")

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdHisto()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    scope = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        scope = HistoChart(cmd.batch_mode, cmd.x[0], cmd.x[1], cmd.bin_count, cmd.path, cmd.outfile)

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
            print("histo_chart: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        if cmd is not None and cmd.verbose:
            print(scope, file=sys.stderr)
            print("histo_chart: holding", file=sys.stderr)

        if scope is not None:
            try:
                scope.close()
                scope.hold()

            except RuntimeError:
                pass
