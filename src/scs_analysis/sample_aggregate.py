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
paths can be specified. For each path, a positive integer must also be supplied, indicating the precision to which the
midpoint result should be reported.

The input JSON document must contain a field labelled 'rec', providing an ISO 8601 localised datetime. If this field
is not present then the document is skipped. Note that the timezone of the output rec datetimes is the same as the
input rec values.

If the input document does not contain a specified path - or if the value is null - then the value is ignored. Aside
from null, values must be integers or floats.

At each checkpoint, if there are no values for a given path, then that path is not included in the output report. If
there are no values for any path, then no report is written to stdout.

SYNOPSIS
sample_aggregate.py [-m] [-v] -c HH:MM:SS PATH_1 [.. PATH_N]

EXAMPLES
csv_reader.py gases.csv | sample_aggregate.py -c **:/5:00 val.CO.cnc 1
"""

import sys

from decimal import InvalidOperation

from scs_analysis.cmd.cmd_sample_aggregate import CmdSampleAggregate

from scs_core.data.json import JSONify
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict


# TODO: if no paths are specified, use all - do this for some other utilities...
# TODO: CmdSampleAggregate supplies the nodes, we then use the stdin document to provide the leaf nodes

# --------------------------------------------------------------------------------------------------------------------

class SampleAggregate(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, min_max, nodes):
        """
        Constructor
        """
        self.__min_max = min_max
        self.__nodes = nodes

        self.__regressions = {}

        for node in self.__nodes:
            self.__regressions[node.path] = LinearRegression()


    # ----------------------------------------------------------------------------------------------------------------

    def has_value(self):
        for regression in self.__regressions.values():
            if regression.has_midpoint():
                return True

        return False


    def append(self, datetime, sample):
        for node in self.__nodes:
            try:
                value = sample.node(node.path)

            except KeyError:
                continue

            if value is not None:
                try:
                    self.__regressions[node.path].append(datetime, value)
                    node.widen_precision(value)

                except InvalidOperation:
                    print("sample_aggregate: non-numeric value for %s: %s" % (node.path, str(value)), file=sys.stderr)
                    exit(1)


    def reset(self):
        for path in self.__regressions.keys():
            self.__regressions[path].reset()


    def report(self, localised_datetime):
        report = PathDict()

        report.append('rec', localised_datetime.as_iso8601())

        for node in self.__nodes:
            path = node.path
            precision = node.precision

            regression = self.__regressions[path]

            if self.__regressions[path].has_midpoint():
                _, midpoint = regression.midpoint()

                if self.__min_max:
                    report.append(path + '.min', round(regression.min(), precision))
                    report.append(path + '.mid', round(midpoint, precision))
                    report.append(path + '.max', round(regression.max(), precision))

                else:
                    report.append(path, round(midpoint, precision))

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

        aggregate = SampleAggregate(cmd.min_max, cmd.nodes)

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
