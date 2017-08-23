#!/usr/bin/env python3

"""
Created on 23 Aug 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./socket_receiver.py | ./sample_regression.py val.sht.tmp -t 4
"""


import sys

from scs_analysis.cmd.cmd_sample_aggregate import CmdSampleAggregate

from scs_core.data.json import JSONify
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict

from scs_core.sys.exception_report import ExceptionReport


# --------------------------------------------------------------------------------------------------------------------

class SampleRegression(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, path, tally):
        """
        Constructor
        """
        self.__path = path
        self.__func = LinearRegression(tally, True)


    # ----------------------------------------------------------------------------------------------------------------

    def datum(self, sample):
        if not sample.has_path(self.__path):
            return None

        rec = LocalizedDatetime.construct_from_jdict(sample.node('rec'))
        value = sample.node(self.__path)

        self.__func.append(rec, value)

        if not self.__func.has_tally():
            return None

        slope, intercept = self.__func.compute()

        if slope is None:
            return None

        target = PathDict()

        target.copy(datum, 'rec')

        target.append(self.__path + '.src', value)
        target.append(self.__path + '.slope', round(slope * 60 * 60, 6))        # x-scale is hours
        target.append(self.__path + '.intercept', round(intercept, 6))

        return target.node()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "SampleRegression:{path:%s, func:%s}" % (self.__path, self.__func)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleAggregate()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        sampler = SampleRegression(cmd.path, cmd.tally)

        if cmd.verbose:
            print(sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                break

            average = sampler.datum(datum)

            if average is not None:
                print(JSONify.dumps(average))
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_regression: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
