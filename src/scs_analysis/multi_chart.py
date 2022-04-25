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

Depending on operating system, it may be necessary to use a matplotlibrc file, which specifies the Matplotlib
back-end graphics system.

SYNOPSIS
multi_chart.py [-b] [-x POINTS] [-y MIN MAX] [-e] [-t TITLE] [-v] PATH_1 .. PATH_N

EXAMPLES
socket_receiver.py | multi_chart.py val.opc_n2.pm10 val.opc_n2.pm2p5 val.opc_n2.pm1 -x 120 -e

FILES
~/SCS/scs_analysis/src/scs_analysis/matplotlibrc

SEE ALSO
scs_analysis/histo_chart
scs_analysis/single_chart

BUGS
On some operating systems, the chart will remain as the uppermost window until all data have been received.
"""

import sys
import warnings

from scs_analysis.chart.multi_chart import MultiChart
from scs_analysis.cmd.cmd_multi_chart import CmdMultiChart

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.sync.line_reader import LineReader

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    warnings.filterwarnings("ignore", module="matplotlib")

    chart = None
    proc = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdMultiChart()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('multi_chart', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # reader...
        reader = LineReader(sys.stdin.fileno())
        logger.info(reader)

        # chart...
        chart = MultiChart(cmd.title, cmd.batch_mode, cmd.x, cmd.y[0], cmd.y[1], *cmd.paths)
        logger.info(chart)
        logger.info("backend: %s" % chart.backend())

        logger.error("terminate this utility by closing the chart window.")


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

            for path in cmd.paths:
                if path not in datum.paths():
                    if not cmd.skip_malformed:
                        logger.error("path: %s not in %s" % (path, line.strip()))
                        exit(1)

                    continue

                try:
                    float(datum.node(path))
                except ValueError:
                    logger.error("invalid value for path: %s: %s" % (path, line.strip()))
                    exit(1)

            if cmd.echo:
                print(JSONify.dumps(datum))
                sys.stdout.flush()

            chart.plot(datum)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if not chart.closed:
            chart.render()

    except KeyboardInterrupt:
        print(file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        if proc:
            proc.terminate()

        if chart is not None and not chart.closed:
            logger.info("closing.")
            chart.close(None)
