#!/usr/bin/env python3

"""
Created on 4 Mar 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_regression utility provides a statical report on a single specified field for documents provided in the
input data stream. The specified field(s) normally represent an error or difference between two sources.

If the specified field(s) are not present in any of the input documents, the sample_regression utility terminates.
If a field is present but cannot be interpreted as a float, that document is ignored.

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
* Median
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
sample_stats.py [-t] [-p PRECISION] [-a] [-r] [-v] PATH1 [PATH2 .. PATHN]

EXAMPLES
csv_reader.py -v scs-bgx-621-gases-2022-07-04-1min.csv | \
sample_stats.py -t -p1 -a val.VOC.cnc val.CO2.cnc exg.val.NO2.cnc | \
csv_writer.py -e scs-bgx-621-gases-2022-07-04-1min-stats.csv

DOCUMENT EXAMPLE - INPUT
{"ref": {"gas": {"SO2": 4.1}}, "SO2": {"vE": {"Urban": {"22Q1": 1.9}}},
"err": {"SO2": {"vE": {"Urban": {"22Q1": -2.2}}}}}
...

DOCUMENT EXAMPLE - OUTPUT
standard mode:
{"tag": "scs-bgx-619", "val": {"VOC": {"cnc": {"count": 4320, "min": 397.7, "mean": 448.2, "median": 446.1,
"max": 498.9, "var": 375.6, "stdev": 19.4, "stdev2": 38.8, "stdev3": 58.2}}}}

analytic mode:
{"tag": "scs-bgx-570", "val": {"SO2": {"cnc": {"min": -3.6, "mean": 1.7, "median": 1.4, "max": 9.3,
"l3": -5.8, "l2": -3.4, "l1": -1.0, "u1": 3.8, "u2": 6.2, "u3": 8.6, "a1": 4.8, "a2": 9.6, "a3": 14.4}

rows mode:
{"path": "val.NO2.cnc", "count": 60, "min": 13.1, "mean": 21.0, "median": 20.3, "max": 35.4, "var": 16.3,
"stdev": 4.0, "stdev2": 8.0, "stdev3": 12.0}
{"path": "val.Ox.cnc", "count": 60, "min": 98.9, "mean": 110.6, "median": 111.2, "max": 117.5, "var": 17.5,
"stdev": 4.2, "stdev2": 8.4, "stdev3": 12.6}
{"path": "val.NO.cnc", "count": 60, "min": 18.1, "mean": 28.1, "median": 25.4, "max": 69.7, "var": 92.0,
"stdev": 9.6, "stdev2": 19.2, "stdev3": 28.8}

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
        values = {path: [] for path in cmd.paths}

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            if cmd.include_tag and tag is None:
                try:
                    tag = datum.node(cmd.tag)
                except KeyError:
                    tag = None

            document_count += 1

            for path in cmd.paths:
                if not datum.has_path(path):
                    logger.error("path '%s' not in datum: %s" % (path, line.strip()))
                    exit(1)

                try:
                    values[path].append(float(datum.node(path)))
                except ValueError:
                    continue

            processed_count += 1

        # validation...
        for path in cmd.paths:
            if len(values[path]) < 2:
                logger.error("at least two valid input documents are required for '%s'." % path)
                exit(1)

        # stats...
        report = PathDict()

        for path in cmd.paths:
            stats = Stats.construct(values[path], prec=cmd.precision)

            if cmd.analytic:
                stats = StatsAnalysis.construct_from_stats(stats, prec=cmd.precision)

            logger.info("%s: %s" % (path, stats))

            # output...
            stats_dict = PathDict(stats.as_json())

            if cmd.include_tag:
                report.append('tag', tag)

            if cmd.rows:
                report.append('path', path)
                for stats_path in stats_dict.paths():
                    report.append(stats_path, stats_dict.node(stats_path))

                print(JSONify.dumps(report))

            else:
                for stats_path in stats_dict.paths():
                    report.append('.'.join((path, stats_path)), stats_dict.node(stats_path))

        if not cmd.rows:
            print(JSONify.dumps(report))


# ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        logger.info("documents: %d processed: %d" % (document_count, processed_count))
