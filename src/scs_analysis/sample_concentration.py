#!/usr/bin/env python3

"""
Created on 16 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_concentration utility is used to inject an absolute humidity (aH) value into any JSON document that contains
relative humidity (rH) and temperature (t) fields.

rH must be presented as a percentage, and t as degrees Centigrade. The generated aH value is presented in
grammes per cubic metre. If fields are missing from the input document, then the document is ignored. If values are
malformed, execution will terminate.

All fields in the input document are presented in the output document, with the exception of the rH field - the rH
leaf node is recreated as the dictionary {rh: RH_VALUE, ah: AH_VALUE} - see example below.

The conversion equation used by sample_concentration does not take account of atmospheric pressure.

SYNOPSIS
sample_concentration.py [-p PRESSURE] [-v] GAS DENSITY_PATH T_PATH [P_PATH]

EXAMPLES
csv_reader.py reference_gases.csv | sample_concentration.py val.hmd val.tmp

DOCUMENT EXAMPLE - INPUT
{"val": {"hmd": 54.5, "tmp": 23.6, "bar": {"p0": 103.2, "pA": 102, "tmp": 23.3}},
"rec": "2019-02-16T13:53:52Z", "tag": "scs-ap1-6"}

DOCUMENT EXAMPLE - OUTPUT
{"val": {"hmd": {"rH": 54.5, "aH": 11.6}, "tmp": 23.6, "bar": {"p0": 103.2, "pA": 102, "tmp": 23.3}},
"rec": "2019-02-16T13:53:52Z", "tag": "scs-ap1-6"}

RESOURCES
https://github.com/south-coast-science/scs_dev/wiki/3:-Data-formats
https://www.aqua-calc.com/calculate/humidity
"""

import sys

from scs_analysis.cmd.cmd_sample_concentration import CmdSampleConcentration

from scs_core.climate.absolute_humidity import AbsoluteHumidity

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.gas.gas import Gas


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleConcentration()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if not Gas.is_valid_name(cmd.gas):
        print("sample_concentration: the gas '%s' is not recognised." % cmd.gas, file=sys.stderr)
        exit(1)

    if cmd.verbose:
        print("sample_concentration: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # density / t...
            if cmd.density_path not in paths or cmd.t_path not in paths:
                continue

            density_node = datum.node(cmd.density_path)
            t_node = datum.node(cmd.t_path)

            if density_node == '' or t_node == '':
                continue

            try:
                density = float(density_node)
            except ValueError:
                rh = None
                print("sample_concentration: invalid value for density in %s" % jstr, file=sys.stderr)
                exit(1)

            try:
                t = float(t_node)
            except ValueError:
                t = None
                print("sample_concentration: invalid value for t in %s" % jstr, file=sys.stderr)
                exit(1)

            # ah = round(AbsoluteHumidity.from_rh_t(rh, t), 1)

            target = PathDict()

            # copy...
            for path in paths:
                if path == cmd.rh_path:
                    target.append(path + '.rH', rh)
                    target.append(path + '.aH', ah)

                else:
                    target.append(path, datum.node(path))

            # report...
            print(JSONify.dumps(target.node()))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_concentration: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_concentration: documents: %d processed: %d" % (document_count, processed_count),
                  file=sys.stderr)
