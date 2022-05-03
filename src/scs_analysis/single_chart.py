#!/usr/bin/env python3

"""
Created on 21 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The single_chart utility is used to display a Matplotlib categorical chart for one or more data sources. Data is
provided by a sequence of JSON documents on stdin. The charting source is specified by a path to a leaf node in the
JSON document.

An optional "batch" ("-b") flag can be set, causing the plotting only to take place when all data points have been
received.

A "relative" ("-r") option ploys the first data point at y position zero, and all subsequent points relative to the
first point. This is useful when examining noise on a signal whose absolute values may be far from zero.

Note that the chart is a simple approximation to a timeline chart - values are plotted successively, with no account
taken of the interval between samples.

Depending on operating system, it may be necessary to use a matplotlibrc file, which specifies the Matplotlib
back-end graphics system.

SYNOPSIS
single_chart.py [-b] [-r] [-x POINTS] [-y MIN MAX] [-e] [-t TITLE] [-v] [PATH]

EXAMPLES
socket_receiver.py | single_chart.py -r val.afe.sns.CO.cnc

FILES
~/SCS/scs_analysis/src/scs_analysis/matplotlibrc

SEE ALSO
scs_analysis/histo_chart
scs_analysis/multi_chart

BUGS
On some operating systems, the chart will remain as the uppermost window until all data have been received.
"""

import sys
import warnings

from scs_analysis.chart.single_chart import SingleChart
from scs_analysis.cmd.cmd_single_chart import CmdSingleChart

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

    cmd = CmdSingleChart()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('single_chart', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # reader...
        reader = LineReader(sys.stdin.fileno())
        logger.info(reader)

        # chart...
        chart = SingleChart(cmd.title, cmd.batch_mode, cmd.x, cmd.y[0], cmd.y[1], cmd.relative, cmd.path)
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

            if cmd.path not in datum.paths():
                if not cmd.skip_malformed:
                    logger.error("path: %s not in %s" % (cmd.path, line.strip()))
                    exit(1)

                continue

            try:
                float(datum.node(cmd.path))
            except ValueError:
                logger.error("invalid value for path: %s: %s" % (cmd.path, line.strip()))
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
