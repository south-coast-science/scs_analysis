#!/usr/bin/env python3

"""
Created on 16 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_ah utility may be used to inject an absolute humidity (aH) value into any JSON document that contains
relative humidity (rH) and temperature (t) fields.

rH must be presented as a percentage, and t as degrees Centigrade. The generated aH value is presented in
grammes per cubic metre. If fields are missing from the input document or are malformed, execution will terminate.

All fields in the input document are presented in the output document, with the exception of the rH field - the rH
leaf node is recreated as the dictionary {rh: RH_VALUE, ah: AH_VALUE} - see example below.

The conversion equation used by sample_ah does not take account of atmospheric pressure.

SYNOPSIS
sample_ah.py [-v] RH_PATH T_PATH

EXAMPLES
csv_reader.py climate.csv | sample_ah.py val.hmd val.tmp

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

from scs_analysis.cmd.cmd_sample_ah import CmdSampleAH

from scs_core.climate.absolute_humidity import AbsoluteHumidity

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleAH()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_ah: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            paths = datum.paths()

            # rH / t...
            if cmd.rh_path not in paths:
                print("sample_ah: rH path '%s' not in %s" % (cmd.rh_path, jstr), file=sys.stderr)
                exit(1)

            if cmd.t_path not in paths:
                print("sample_ah: t path '%s' not in %s" % (cmd.t_path, jstr), file=sys.stderr)
                exit(1)

            rh = datum.node(cmd.rh_path)
            t = datum.node(cmd.t_path)

            # aH...
            ah = AbsoluteHumidity.from_rh_t(rh, t)

            target = PathDict()

            # copy...
            for path in paths:
                if path == cmd.rh_path:
                    target.append(path + '.rH', rh)
                    target.append(path + '.aH', round(ah, 1))

                else:
                    target.append(path, datum.node(path))

            # report...
            print(JSONify.dumps(target.node()))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_ah: KeyboardInterrupt", file=sys.stderr)
