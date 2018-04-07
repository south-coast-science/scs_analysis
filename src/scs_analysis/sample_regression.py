#!/usr/bin/env python3

"""
Created on 23 Aug 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_regression utility computes a linear regression for a stream of data delivered on stdin.

Input data is typically in the form of a JSON document. A command parameter specifies the path to the node within
the document that is to be averaged. The node is typically a leaf node integer or float. The output of the
sample_regression utility includes the last source value, slope and intercept.

SYNOPSIS
sample_regression.py [-t TALLY] [-p PRECISION] [-v] [PATH]

EXAMPLES
./osio_topic_history.py -m60 /orgs/south-coast-science-demo/brighton/loc/1/gases | \
./sample_regression.py -t360 -p3 val.CO.cnc

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-bgx-401", "rec": "2018-03-27T09:54:41.042+00:00", "val": {
"NO2": {"weV": 0.29563, "aeV": 0.280879, "weC": 0.009569, "cnc": 61.0},
"Ox": {"weV": 0.406819, "aeV": 0.387443, "weC": -0.010706, "cnc": 34.7},
"NO": {"weV": 0.319692, "aeV": 0.292129, "weC": 0.028952, "cnc": 165.5},
"CO": {"weV": 0.395819, "aeV": 0.289317, "weC": 0.113108, "cnc": 311.3},
"sht": {"hmd": 82.4, "tmp": 12.6}}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2018-03-27T16:10:51.033+00:00", "val": {"CO": {"cnc": {"src": 202.5, "slope": 0.039, "intercept": 226.217}}}}
"""


import sys

from scs_analysis.cmd.cmd_sample_aggregate import CmdSampleAggregate

from scs_core.data.json import JSONify
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

class SampleRegression(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, path, tally, precision):
        """
        Constructor
        """
        self.__path = path
        self.__precision = precision

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

        if sample.has_path('rec'):
            target.copy(sample, 'rec')

        target.append(self.__path + '.src', value)
        target.append(self.__path + '.slope', round(slope, self.__precision))
        target.append(self.__path + '.intercept', round(intercept, self.__precision))

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

        sampler = SampleRegression(cmd.path, cmd.tally, cmd.precision)

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
