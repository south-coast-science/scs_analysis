#!/usr/bin/env python3

"""
Created on 13 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./socket_receiver.py | ./sample_roll.py val.sht.tmp -c 4
"""


import sys

from scs_analysis.cmd.cmd_sample_roll import CmdSampleRoll

from scs_core.data.path_dict import PathDict
from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport


# TODO: should deal with list of paths

# --------------------------------------------------------------------------------------------------------------------

class SampleRoll(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, count, path):
        """
        Constructor
        """
        self.__count = count
        self.__path = path

        self.__points = [None] * count


    # ----------------------------------------------------------------------------------------------------------------

    def datum(self, datum):
        latest = float(datum.node(self.__path))

        self.__add_point(latest)
        avg = self.__avg()

        if avg is None:
            return None

        target = PathDict()

        target.copy('rec')

        target.append(self.__path + '.src', latest)
        target.append(self.__path + '.avg', round(avg, 6))

        return target.node()


    # ----------------------------------------------------------------------------------------------------------------

    def __add_point(self, point):
        del self.__points[0]

        self.__points.append(point)


    def __avg(self):
        total = 0

        for i in range(self.__count):
            if self.__points[i] is None:
                return None

            total += self.__points[i]

        return total / self.__count


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def points(self):
        return self.__points


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "SampleRoll:{count:%d, path:%s, aggregate:%s}" % (self.__count, self.__path, self.points)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleRoll()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        roll = SampleRoll(cmd.count, cmd.path)

        if cmd.verbose:
            print(roll, file=sys.stderr)


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

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("sample_roll: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
