#!/usr/bin/env python3

"""
Created on 19 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_noise utility is typically used in a setting where data has a gaussian distribution around a fixed or
slow-moving value. The error analysis shows the difference between the current value, and an exponential
average.

Input data is typically in the form of a JSON document. A command parameter specifies the path to the node within
the document that is to be examined. The node is typically a leaf node integer or float. The output of the
sample_noise utility includes the source value, aggregate, and the error.

SYNOPSIS
sample_noise.py [-p PRECISION] [-v] [PATH]

EXAMPLES
aws_topic_history.py -t 10 /orgs/south-coast-science-demo/brighton/loc/1/gases | sample_noise.py -p 3 val.CO.cnc

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-bgx-401", "rec": "2018-03-27T09:54:41.042+00:00", "val": {
"NO2": {"weV": 0.29563, "aeV": 0.280879, "weC": 0.009569, "cnc": 61.0},
"Ox": {"weV": 0.406819, "aeV": 0.387443, "weC": -0.010706, "cnc": 34.7},
"NO": {"weV": 0.319692, "aeV": 0.292129, "weC": 0.028952, "cnc": 165.5},
"CO": {"weV": 0.395819, "aeV": 0.289317, "weC": 0.113108, "cnc": 311.3},
"sht": {"hmd": 82.4, "tmp": 12.6}}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2018-03-27T10:07:11.033+00:00", "val": {"CO": {"cnc": {"src": 263.0, "agr": 194.69, "err": 68.31}}}}
"""

import sys

from scs_analysis.cmd.cmd_sample_filter import CmdSampleFilter

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

class SampleNoise(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, path, precision):
        """
        Constructor
        """
        self.__path = path
        self.__precision = precision

        self.__aggregate = None


    # ----------------------------------------------------------------------------------------------------------------

    def datum(self, sample):
        latest = float(sample.node(self.__path))

        if self.__aggregate is None:
            self.__aggregate = latest
            return None

        self.__aggregate = (0.9 * self.__aggregate) + (0.1 * latest)
        error = latest - self.__aggregate

        target = PathDict()

        if sample.has_path('rec'):
            target.copy(sample, 'rec')

        target.append(self.__path + '.src', latest)
        target.append(self.__path + '.agr', round(self.__aggregate, self.__precision))
        target.append(self.__path + '.err', round(error, self.__precision))

        return target.node()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def aggregate(self):
        return self.__aggregate


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        aggregate = "None" if self.__aggregate is None else format(self.__aggregate, '.6f')

        return "SampleNoise:{path:%s, precision:%s, aggregate:%s}" % (self.__path, self.__precision, aggregate)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleFilter()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_noise: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        err = SampleNoise(cmd.path, cmd.precision)

        if cmd.verbose:
            print("sample_noise: %s" % err, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            document_count += 1

            error_datum = err.datum(datum)

            if error_datum is not None:
                print(JSONify.dumps(error_datum))
                sys.stdout.flush()

            processed_count += 1

        if cmd.verbose:
            print(err, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_noise: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
