#!/usr/bin/env python3

"""
Created on 24 Oct 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_aggregate utility is used to

SYNOPSIS
sample_aggregate.py [-v] -c HH:MM:SS PATH_1 .. PATH_N

EXAMPLES
sample_aggregate.py -c **:**:00 val.CO.cnc
"""

import sys

from scs_analysis.cmd.cmd_sample_aggregate import CmdSampleAggregate

from scs_core.data.json import JSONify
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict


# TODO: add precision control

# --------------------------------------------------------------------------------------------------------------------

class SampleAggregate(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, paths):
        """
        Constructor
        """
        self.__paths = paths

        self.__regressions = {}

        for path in self.__paths:
            self.__regressions[path] = LinearRegression()


    # ----------------------------------------------------------------------------------------------------------------

    def has_midpoint(self):
        for regression in self.__regressions.values():
            if regression.has_midpoint():
                return True

        return False


    def append(self, sample):
        for path in self.__paths:
            value = sample.node(path)

            if value is not None:
                self.__regressions[path].append(rec, value)


    def reset(self):
        for path in self.__regressions.keys():
            self.__regressions[path].reset()


    def report(self, localised_datetime):
        aggregate = PathDict()

        aggregate.append('rec', localised_datetime.as_iso8601())

        for path, regression in self.__regressions.items():
            if regression.has_midpoint():
                _, midpoint_val = regression.midpoint()

                aggregate.append(path, round(midpoint_val, 6))

        return aggregate


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        regressions = '[' + ', '.join(path + ':' + str(reg) for path, reg in self.__regressions.items()) + ']'

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

        sampler = SampleAggregate(cmd.paths)

        if cmd.verbose:
            print("sample_aggregate: %s" % sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        checkpoint = None

        for line in sys.stdin:
            # sample...
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            # set checkpoint...
            rec = LocalizedDatetime.construct_from_iso8601(datum.node('rec'))

            if checkpoint is None:
                checkpoint = generator.next_localised_datetime(rec)

            # report & reset...
            if rec.datetime > checkpoint.datetime:
                if sampler.has_midpoint():
                    print(JSONify.dumps(sampler.report(checkpoint)))
                    sys.stdout.flush()

                    sampler.reset()

                checkpoint = generator.next_localised_datetime(rec)

            # append sample...
            sampler.append(datum)

        # report remainder...
        if sampler.has_midpoint():
            print(JSONify.dumps(sampler.report(checkpoint)))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_aggregate: KeyboardInterrupt", file=sys.stderr)
