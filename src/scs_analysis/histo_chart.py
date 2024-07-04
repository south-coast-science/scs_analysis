#!/usr/bin/env python3

"""
Created on 3 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The histo_chart utility is used to create Matplotlib histogram charts and comma-separated value (CSV) histogram files.
The utility analyses a given path to a leaf node of the input JSON data stream.

For the domain MIN and MAX flag, a value is included if:

MIN <= value < MAX

An optional "batch" ("-b") flag can be set, causing the plotting only to take place when all data points have been
received.

On Linux, it may be necessary to install tkinter in order for the chart to be displayed:
sudo apt-get install python3-tk

Depending on operating system, it may be necessary to use a matplotlibrc file, which specifies the Matplotlib
back-end graphics system.

SYNOPSIS
histo_chart.py [-b] [-x MIN MAX] [-c BIN_COUNT] [-p PRECISION] [-o FILENAME] [-e] [-t TITLE] [-v] PATH

EXAMPLES
socket_receiver.py | histo_chart.py val.CO2.cnc -x -10 10 -e -o CO2.csv

FILES
~/SCS/scs_analysis/src/scs_analysis/matplotlibrc

SEE ALSO
scs_analysis/multi_chart
scs_analysis/single_chart

RESOURCES
https://matplotlib.org/2.0.2/faq/usage_faq.html#what-is-a-backend
https://stackoverflow.com/questions/56656777/userwarning-matplotlib-is-currently-using-agg-which-is-a-non-gui-backend-so

BUGS
On some operating systems, the chart will remain as the uppermost window until all data have been received.
"""

import sys
import warnings

from scs_analysis.chart.histo_chart import HistoChart
from scs_analysis.cmd.cmd_histo_chart import CmdHistoChart

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

    cmd = CmdHistoChart()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('histo_chart', verbose=cmd.verbose)
    logger = Logging.getLogger()

    if cmd.bin_count < 1:
        logger.error("bin count must be greater than 0.")
        exit(2)

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # reader...
        reader = LineReader(sys.stdin.fileno())

        # chart...
        chart = HistoChart(cmd.title, cmd.batch_mode, cmd.x[0], cmd.x[1], cmd.bin_count, cmd.precision, cmd.path,
                           outfile=cmd.outfile)
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
                continue

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
