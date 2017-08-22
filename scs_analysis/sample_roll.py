#!/usr/bin/env python3

"""
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./socket_receiver.py | ./sample_roll.py val.sht.tmp -t 4
"""


import sys

from scs_analysis.cmd.cmd_sample_smooth import CmdSampleSmooth

from scs_core.data.path_dict import PathDict
from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport


# --------------------------------------------------------------------------------------------------------------------

class SampleRoll(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, path, tally):
        """
        Constructor
        """
        self.__path = path
        self.__tally = tally

        self.__points = [None] * tally if tally else []


    # ----------------------------------------------------------------------------------------------------------------

    def datum(self, datum):
        latest = float(datum.node(self.__path))

        self.__add_point(latest)
        avg = self.__avg()

        if avg is None:
            return None

        target = PathDict()

        target.copy(datum, 'rec')

        target.append(self.__path + '.src', latest)
        target.append(self.__path + '.avg', round(avg, 6))

        return target.node()


    # ----------------------------------------------------------------------------------------------------------------

    def __add_point(self, point):
        if self.__tally is not None:
            del self.__points[0]

        self.__points.append(point)


    def __avg(self):
        total = 0
        count = 0

        for point in self.__points:
            if point is None:
                return None

            total += point
            count += 1

        return total / count


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def points(self):
        return self.__points


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "SampleRoll:{path:%s, tally:%d, points:%s}" % (self.__path, self.__tally, self.points)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleSmooth()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        roll = SampleRoll(cmd.path, cmd.tally)

        if cmd.verbose:
            print(roll, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            sample_datum = PathDict.construct_from_jstr(line)

            if sample_datum is None:
                break

            avg_datum = roll.datum(sample_datum)

            if avg_datum is not None:
                print(JSONify.dumps(avg_datum))
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_roll: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
