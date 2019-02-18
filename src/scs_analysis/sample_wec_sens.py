#!/usr/bin/env python3

"""
Created on 16 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_wec_sens utility may be used to

SYNOPSIS
sample_wec_sens.py [-v] RH_PATH T_PATH

EXAMPLES
csv_reader.py climate.csv | sample_wec_sens.py val.hmd val.tmp

DOCUMENT EXAMPLE - INPUT
{"val": {"hmd": 54.5, "tmp": 23.6, "bar": {"p0": 103.2, "pA": 102, "tmp": 23.3}},
"rec": "2019-02-16T13:53:52Z", "tag": "scs-ap1-6"}

DOCUMENT EXAMPLE - OUTPUT
{"val": {"hmd": {"rH": 54.5, "aH": 11.6}, "tmp": 23.6, "bar": {"p0": 103.2, "pA": 102, "tmp": 23.3}},
"rec": "2019-02-16T13:53:52Z", "tag": "scs-ap1-6"}

RESOURCES
https://www.aqua-calc.com/calculate/humidity
"""

import sys

from scs_analysis.cmd.cmd_sample_wec_sens import CmdSampleWeCSens

from scs_core.climate.absolute_humidity import AbsoluteHumidity

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    wec = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleWeCSens()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_wec_sens: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        wec_path = cmd.path + '.weC'
        wec_sens_path = cmd.path + '.weC_sens'


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            paths = datum.paths()

            # weC...
            if wec_path not in paths:
                continue

            wec_node = datum.node(wec_path)

            if wec_node == '':
                continue

            try:
                wec = float(wec_node)
            except ValueError:
                rh = None
                print("sample_wec_sens: invalid value for %s in %s" % (wec_path, jstr), file=sys.stderr)
                exit(1)

            wec_sens = round(wec / (cmd.sens / 1000), 1)

            target = PathDict()

            # copy...
            for path in paths:
                if path == wec_sens_path:
                    continue                                        # ignore any existing wec_sens_path

                if path == wec_path:
                    target.append(wec_path, wec)
                    target.append(wec_sens_path, wec_sens)

                else:
                    target.append(path, datum.node(path))

            # report...
            print(JSONify.dumps(target.node()))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_wec_sens: KeyboardInterrupt", file=sys.stderr)
