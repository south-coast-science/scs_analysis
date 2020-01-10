#!/usr/bin/env python3

"""
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The multi_chart utility is used to display a Matplotlib categorical chart for one or more data sources. The
data sources share a common y-axis scale. Data is provided by a sequence of JSON documents on stdin. Each charting
source is specified by a path to a leaf node in the JSON document.

An optional "batch" ("-b") flag can be set, causing the plotting only to take place when all data points have been
received.

Note that the chart is a simple approximation to a timeline chart - values are plotted successively, with no account
taken of the interval between samples.

Depending on operating system, it may be necessary to edit the matplotlibrc file, which specifies the Matplotlib
back-end graphics system.

SYNOPSIS
multi_chart.py [-b] [-x POINTS] [-y MIN MAX] [-e] [-v] PATH_1 .. PATH_N

EXAMPLES
socket_receiver.py | multi_chart.py val.opc_n2.pm10 val.opc_n2.pm2p5 val.opc_n2.pm1 -x 120 -e

FILES
~/SCS/scs_analysis/src/scs_analysis/matplotlibrc

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
        print("multi_chart: %s" % cmd, file=sys.stderr)

    chart = None
    proc = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # reader...
        reader = LineReader(sys.stdin.fileno())

        if cmd.verbose:
            print("multi_chart: %s" % reader, file=sys.stderr)

        # chart...
        chart = MultiChart(cmd.batch_mode, cmd.x, cmd.y[0], cmd.y[1], *cmd.paths)

        if cmd.verbose:
            print("multi_chart: %s" % chart, file=sys.stderr)
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
                print(JSONify.dumps(datum))
                sys.stdout.flush()

            chart.plot(datum)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("multi_chart: KeyboardInterrupt", file=sys.stderr)


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
