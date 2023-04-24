#!/usr/bin/env python3

"""
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_average utility is used to compute an average value for a stream of data delivered on stdin. This can be an
average of all values, or a rolling average for a given number of values.

Input data is typically in the form of a JSON document. A command parameter specifies the path to the node within
the document that is to be averaged. The node is typically a leaf node integer or float. The output of the
sample_average utility includes the source value, and the average value.

SYNOPSIS
sample_average.py [-t TALLY] [-p PRECISION] [-v] [PATH]

EXAMPLES
aws_topic_history.py -m1 /orgs/south-coast-science-demo/brighton/loc/1/gases | sample_average.py -t3 -p1 val.CO.cnc

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-bgx-401", "rec": "2018-03-27T09:54:41.042+00:00", "val": {
"NO2": {"weV": 0.29563, "aeV": 0.280879, "weC": 0.009569, "cnc": 61.0},
"Ox": {"weV": 0.406819, "aeV": 0.387443, "weC": -0.010706, "cnc": 34.7},
"NO": {"weV": 0.319692, "aeV": 0.292129, "weC": 0.028952, "cnc": 165.5},
"CO": {"weV": 0.395819, "aeV": 0.289317, "weC": 0.113108, "cnc": 311.3},
"sht": {"hmd": 82.4, "tmp": 12.6}}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2018-03-27T10:01:21.028+00:00", "val": {"CO": {"cnc": {"src": 145.6, "avg": 168.2}}}}
"""

import sys

from scs_analysis.cmd.cmd_sample_tally import CmdSampleTally

from scs_core.data.average import Average
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

class SampleAverage(object):
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

        self.__func = Average(tally)


    # ----------------------------------------------------------------------------------------------------------------

    def datum(self, sample):
        if not sample.has_path(self.__path):
            return None

        value = sample.node(self.__path)
        self.__func.append(value)

        avg = self.__func.mid()

        if avg is None:
            return None

        target = PathDict()

        if sample.has_path('rec'):
            target.copy(sample, 'rec')

        target.append(self.__path + '.src', value)
        target.append(self.__path + '.avg', round(avg, self.__precision))

        return target.node()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "SampleAverage:{path:%s, precision:%s, func:%s}" % (self.__path, self.__precision, self.__func)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleTally()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_average: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        sampler = SampleAverage(cmd.path, cmd.tally, cmd.precision)

        if cmd.verbose:
            print("sample_average: %s" % sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            document_count += 1

            average = sampler.datum(datum)

            if average is not None:
                print(JSONify.dumps(average))
                sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        print("sample_average: %s" % repr(ex), file=sys.stderr)
        exit(1)

    finally:
        if cmd.verbose:
            print("sample_average: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
