#!/usr/bin/env python3

"""
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The multi_chart utility is used to display a Matplotlib timeline chart for one or more data sources. The data sources
share a common y-axis scale. Data is provided by a sequence of JSON documents on stdin. Each charting source is
specified by a path to a leaf node in the JSON document.

EXAMPLES
./socket_receiver.py | ./multi_chart.py val.opc.pm10 val.opc.pm2p5 val.opc.pm1 -x 120 -e

SEE ALSO
scs_analysis/histo_chart
scs_analysis/single_chart
"""

import sys
import warnings

from scs_analysis.chart.multi_chart import MultiChart
from scs_analysis.cmd.cmd_multi_chart import CmdMultiChart

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.sync.line_reader import LineReader

from scs_core.sys.exception_report import ExceptionReport


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    warnings.filterwarnings("ignore", module="matplotlib")

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMultiChart()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    chart = None
    proc = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # reader...
        reader = LineReader(sys.stdin.fileno())

        if cmd.verbose:
            print(reader, file=sys.stderr)

        # chart...
        chart = MultiChart(cmd.batch_mode, cmd.x, cmd.y[0], cmd.y[1], *cmd.paths)

        if cmd.verbose:
            print(chart, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        proc = reader.start()

        for line in reader.lines:
            if chart.closed:
                break

            if line is None:
                chart.pause()
                continue

            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                break

            if cmd.echo:
                print(JSONify.dumps(datum.node()))
                sys.stdout.flush()

            chart.plot(datum)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("multi_chart: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        if proc:
            proc.terminate()

        if chart is not None and not chart.closed:
            if cmd.verbose:
                print("multi_chart: holding", file=sys.stderr)

            # noinspection PyBroadException

            try:
                chart.hold()

            except Exception:
                pass
