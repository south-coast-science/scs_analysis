#!/usr/bin/env python3

"""
Created on 19 Aug 2016

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
./socket_receiver.py | ./sample_conv.py val.afe.sns.CO -s 0.321 \
| ./sample_error.py val.afe.sns.CO.conv
"""

import sys

from scs_analysis.cmd.cmd_sample_filter import CmdSampleFilter

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.sys.exception_report import ExceptionReport


# TODO: should deal with list of paths

# --------------------------------------------------------------------------------------------------------------------

class SampleError(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, path):
        """
        Constructor
        """
        self.__path = path
        self.__aggregate = None


    # ----------------------------------------------------------------------------------------------------------------

    def datum(self, datum):
        latest = float(datum.node(self.__path))

        if self.__aggregate is None:
            self.__aggregate = latest
            return None

        self.__aggregate = (0.9 * self.__aggregate) + (0.1 * latest)
        error = latest - self.__aggregate

        target = PathDict()

        target.copy(datum, 'rec')

        target.append(self.__path + '.src', latest)
        target.append(self.__path + '.agr', round(self.__aggregate, 6))
        target.append(self.__path + '.err', round(error, 6))

        return target.node()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def aggregate(self):
        return self.__aggregate


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        aggregate_fmt = "None" if self.__aggregate is None else format(self.__aggregate, '.6f')

        return "SampleError:{path:%s, aggregate:%s}" % (self.__path, aggregate_fmt)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleFilter()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        err = SampleError(cmd.path)

        if cmd.verbose:
            print(err, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            sample_datum = PathDict.construct_from_jstr(line)

            if sample_datum is None:
                break

            error_datum = err.datum(sample_datum)

            if error_datum is not None:
                print(JSONify.dumps(error_datum))
                sys.stdout.flush()

        if cmd.verbose:
            print(err, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_error: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
