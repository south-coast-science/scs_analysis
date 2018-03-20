#!/usr/bin/env python3

"""
Created on 24 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The XX utility is used to .

EXAMPLES
xx

FILES
~/SCS/aws/

DOCUMENT EXAMPLE
xx

SEE ALSO
scs_analysis/




command line example:
./socket_receiver.py | ./sample_median.py -w 5 val.NO2.cnc
"""

import sys

from scs_analysis.cmd.cmd_sample_median import CmdSampleMedian

from scs_core.data.json import JSONify
from scs_core.data.median_filter import MedianFilter
from scs_core.data.path_dict import PathDict

from scs_core.sys.exception_report import ExceptionReport


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleMedian()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    median_filter = MedianFilter(cmd.window)

    if cmd.verbose:
        print(median_filter, file=sys.stderr)
        sys.stderr.flush()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            sample = PathDict.construct_from_jstr(line)

            if sample is None:
                break

            value = sample.node(cmd.path)

            if value is None:
                break

            target = PathDict()

            if sample.has_path('rec'):
                target.copy(sample, 'rec')

            target.append(cmd.path + '.src', value)
            target.append(cmd.path + '.med', round(median_filter.compute(value), cmd.precision))

            print(JSONify.dumps(target.node()))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_median: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
