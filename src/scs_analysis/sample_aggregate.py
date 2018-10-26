#!/usr/bin/env python3

"""
Created on 24 Oct 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_aggregate utility is used to

SYNOPSIS
sample_aggregate.py [-v] -c HH:MM:SS PATH_1 PRECISION_1 .. PATH_N PRECISION_N

EXAMPLES
sample_aggregate.py -c **:**:00 val.CO.cnc 1
"""

import sys

from scs_analysis.cmd.cmd_sample_aggregate import CmdSampleAggregate

from scs_core.data.json import JSONify
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

class SampleAggregate(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, topics):
        """
        Constructor
        """
        self.__topics = topics

        self.__regressions = {}

        for path in self.__topics.keys():
            self.__regressions[path] = LinearRegression()


    # ----------------------------------------------------------------------------------------------------------------

    def has_value(self):
        for regression in self.__regressions.values():
            if regression.has_midpoint():
                return True

        return False


    def append(self, datetime, sample):
        for path in self.__topics.keys():
            try:
                value = sample.node(path)
            except KeyError:
                continue

            if value is not None:
                self.__regressions[path].append(datetime, value)


    def reset(self):
        for path in self.__regressions.keys():
            self.__regressions[path].reset()


    def report(self, localised_datetime):
        report = PathDict()

        report.append('rec', localised_datetime.as_iso8601())

        for path, precision in self.__topics.items():
            if self.__regressions[path].has_midpoint():
                _, midpoint_val = self.__regressions[path].midpoint()

                report.append(path, round(midpoint_val, precision))

        return report


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        regressions = '[' + ', '.join(topic + ':' + str(reg) for topic, reg in self.__regressions.items()) + ']'

        return "SampleAggregate:{regressions:%s}" % regressions


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

        aggregate = SampleAggregate(cmd.topics)

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
