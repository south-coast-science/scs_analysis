#!/usr/bin/env python3

"""
Created on 24 Oct 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_aggregate utility provides linear regression midpoints for data delivered on stdin, over specified units of
time. It can perform this operation for one or many nodes of the input documents.

When each time checkpoint is encountered in the input stream, the midpoint values - together with min and max, if
requested -  are computed and reported. These values are marked with the datetime indicating the end of that period.
When the input stream is closed, any remaining values are reported and marked with the next checkpoint.

Checkpoints are specified in the form HH:MM:SS, in a format similar to that for crontab:

** - all values
NN - exactly matching NN
/N - every match of N

For example, **:/5:30 indicates 30 seconds past the minute, every 5 minutes, during every hour.

Data sources are specified as a path into the input JSON document in the same format as the node command. Any number of
paths can be specified. If a path to an internal node in the JSON document is specified, then all of the
descendants of that node will be processed.

The input JSON document must contain a field labelled 'rec', providing an ISO 8601 localised datetime. If this field
is not present then the document is skipped. Note that the timezone of the output rec datetimes is the same as the
input rec values.

If the input document does not contain a specified path - or if the value is null - then the value is ignored. Aside
from null, values must be integers or floats.

At each checkpoint, if there are no values for a given path, then that path is not included in the output report. If
there are no values for any path, then no report is written to stdout.

SYNOPSIS
sample_aggregate.py -c HH:MM:SS [-m] [-t] [-v] PATH_1 [.. PATH_N]

EXAMPLES
csv_reader.py gases.csv | sample_aggregate.py -c **:/5:00 val
"""

import sys

from decimal import InvalidOperation

from scs_analysis.cmd.cmd_sample_aggregate import CmdSampleAggregate

from scs_core.data.json import JSONify
from scs_core.data.precision import Precision
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

class SampleAggregate(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, min_max, include_tag, nodes):
        """
        Constructor
        """
        self.__min_max = min_max
        self.__nodes = nodes

        self.__precisions = {}
        self.__regressions = {}

        self.__initialised = False

        self.__include_tag = include_tag
        self.__tag = None


    # ----------------------------------------------------------------------------------------------------------------

    def has_value(self):
        for regression in self.__regressions.values():
            if regression.has_midpoint():
                return True

        return False


    def append(self, datetime: LocalizedDatetime, sample: PathDict):
        # initialise...
        if not self.__initialised:
            for node in self.__nodes:
                try:
                    paths = sample.paths(node)

                except IndexError as ex:
                    paths = None
                    print("sample_aggregate: %s: %s" % (node, ex), file=sys.stderr)
                    sys.stderr.flush()
                    exit(1)

                for path in paths:
                    self.__precisions[path] = Precision()
                    self.__regressions[path] = LinearRegression()

            self.__initialised = True

        # tag...
        if self.__include_tag:
            if sample.has_path('tag'):
                self.__tag = sample.node('tag')

        # process data...
        for path in self.__precisions.keys():
            try:
                value = sample.node(path)

            except KeyError:
                continue

            if value is None:
                continue

            try:
                self.__precisions[path].widen(value)
                self.__regressions[path].append(datetime, value)

            except InvalidOperation:
                print("sample_aggregate: non-numeric value for %s: %s" % (path, str(value)), file=sys.stderr)
                sys.stderr.flush()
                exit(1)


    def reset(self):
        for path in self.__regressions.keys():
            self.__regressions[path].reset()


    def report(self, localised_datetime):
        report = PathDict()

        if self.__tag:
            report.append('tag', self.__tag)

        report.append('rec', localised_datetime.as_iso8601())

        for path, precision in self.__precisions.items():
            regression = self.__regressions[path]

            if self.__regressions[path].has_midpoint():
                _, midpoint = regression.midpoint()

                if self.__min_max:
                    report.append(path + '.min', round(regression.min(), precision.digits))
                    report.append(path + '.mid', round(midpoint, precision.digits))
                    report.append(path + '.max', round(regression.max(), precision.digits))

                else:
                    report.append(path, round(midpoint, precision.digits))

        return report


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        regressions = '[' + ', '.join(topic + ':' + str(reg) for topic, reg in self.__regressions.items()) + ']'

        return "SampleAggregate:{min_max:%s, regressions:%s}" % (self.__min_max, regressions)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleAggregate()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_aggregate: %s" % cmd, file=sys.stderr)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        generator = cmd.checkpoint_generator

        aggregate = SampleAggregate(cmd.min_max, cmd.include_tag, cmd.nodes)

        if cmd.verbose:
            print("sample_aggregate: %s" % aggregate, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        checkpoint = None

        for line in sys.stdin:
            # sample...
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            try:
                rec_node = datum.node('rec')
            except KeyError:
                continue

            rec = LocalizedDatetime.construct_from_iso8601(rec_node)

            # set checkpoint...
            if checkpoint is None:
                checkpoint = generator.next_localised_datetime(rec)

            # report & reset...
            if rec.datetime > checkpoint.datetime:
                if aggregate.has_value():
                    print(JSONify.dumps(aggregate.report(checkpoint)))
                    sys.stdout.flush()

                    aggregate.reset()

                checkpoint = generator.next_localised_datetime(rec)

            # append sample...
            aggregate.append(rec, datum)

        # report remainder...
        if aggregate.has_value():
            print(JSONify.dumps(aggregate.report(checkpoint)))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_aggregate: KeyboardInterrupt", file=sys.stderr)
