#!/usr/bin/env python3

"""
Created on 4 Mar 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_regression utility provides a statical report on a single specified field for documents provided in the
input data stream. The specified field normally represents an error or difference betwen two sources.

If the specified field is not present in any of the input documents, the sample_regression utility terminates. If the
field is present but cannot be interpreted as a float, that document is ignored.

The output is a single JSON document. In standard mode, report fields are:

* Document count
* Minimum
* Mean
* Median
* Maximum
* Variance
* First standard deviation
* Second standard deviation
* Third standard deviation

In analytic mode, report fields are:

* Minimum
* Mean
* Maximum
* Lower boundary of 1st standard deviation
* Lower boundary of 2nd standard deviation
* Lower boundary of 3rd standard deviation
* Upper boundary of 1st standard deviation
* Upper boundary of 2nd standard deviation
* Upper boundary of 3rd standard deviation
* Amplitude by 1st standard deviation
* Amplitude by 2nd standard deviation
* Amplitude by 3rd standard deviation

A minimum of two input documents are required.

SYNOPSIS
sample_stats.py [-t] [-p PRECISION] [-a] [-v] PATH

EXAMPLES
csv_reader.py -v Mfi_so2_vE_22Q1_results_err.csv | \
sample_stats.py -v -p 3 err.SO2.vE.Urban.22Q1 | \
csv_writer.py -v Mfi_so2_vE_22Q1_results_err_stats.csv

DOCUMENT EXAMPLE - INPUT
{"ref": {"gas": {"SO2": 4.1}}, "SO2": {"vE": {"Urban": {"22Q1": 1.9}}},
"err": {"SO2": {"vE": {"Urban": {"22Q1": -2.2}}}}}
...

DOCUMENT EXAMPLE - OUTPUT
standard mode:
{"tag": "scs-bgx-619", "val": {"VOC": {"cnc": {"count": 4320, "min": 397.7, "mean": 448.2, "median": 446.1,
"max": 498.9, "var": 375.6, "stdev": 19.4, "stdev2": 38.8, "stdev3": 58.2}}}}

analytic mode:
{"tag": "scs-bgx-619", "val": {"VOC": {"cnc": {"min": 397.7, "mean": 448.2, "max": 498.9,
"l3": 387.9, "l2": 407.3, "l1": 426.7, "u1": 465.5, "u2": 484.9, "u3": 504.3, "a1": 38.8, "a2": 77.6, "a3": 116.4}}}}

RESOURCES
https://en.wikipedia.org/wiki/Standard_deviation
"""

import sys

from scs_analysis.cmd.cmd_sample_stats import CmdSampleStats

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.data.stats import Stats, StatsAnalysis

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    tag = None
    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleStats()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_stats', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        # data...
        values = []

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            if tag is None:
                tag = datum.node('tag')

            document_count += 1

            if not datum.has_path(cmd.path):
                logger.error("path '%s' not in datum: %s" % (cmd.path, line.strip()))
                exit(1)

            try:
                values.append(float(datum.node(cmd.path)))
            except ValueError:
                continue

            processed_count += 1

        # validation...
        if len(values) < 2:
            logger.error("at least two valid input documents are required.")
            exit(1)

        # stats...
        stats = Stats.construct(values, prec=cmd.precision)

        if cmd.analytic:
            stats = StatsAnalysis.construct_from_stats(stats, prec=cmd.precision)

        logger.info(stats)

        # output...
        stats_dict = PathDict(stats.as_json())
        report = PathDict()

        if cmd.include_tag:
            report.append('tag', tag)

        for stats_path in stats_dict.paths():
            report.append('.'.join((cmd.path, stats_path)), stats_dict.node(stats_path))

        print(JSONify.dumps(report))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        logger.info("documents: %d processed: %d" % (document_count, processed_count))
