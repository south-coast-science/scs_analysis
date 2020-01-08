#!/usr/bin/env python3

"""
Created on 8 Jan 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The gas_exegete utility is used to visualise the predicted arithmetic error of an electrochem sensor device,
for a given exegete and gas, for a given T and rH range.

A list of available gas exegetes can be found using the --help flag.

SYNOPSIS
gas_exegete.py -e EXEGETE -g GAS -r RH_MIN RH_MAX RH_DELTA -t T_MIN T_MAX T_DELTA [-v]

EXAMPLES
gas_exegete.py -v -e sbl1v1 -g NO2 -r 10 90 5 -t -10 40 5 | csv_writer.py -v sbl1v1_rendering.csv

DOCUMENT EXAMPLE - OUTPUT
{"rh": "10 %", "-10 °C": 292.7, "-5 °C": 239.6, ..., "35 °C": -184.9, "40 °C": -238.0}
{"rh": "15 %", "-10 °C": 252.4, "-5 °C": 206.6, ..., "35 °C": -160.1, "40 °C": -206.0}
...
{"rh": "85 %", "-10 °C": 27.3, "-5 °C": 25.6, ..., "35 °C": 11.6, "40 °C": 9.9}
{"rh": "90 %", "-10 °C": 35.4, "-5 °C": 32.7, ..., "35 °C": 11.4, "40 °C": 8.7}

RESOURCES
https://github.com/south-coast-science/scs_core/blob/develop/src/scs_core/gas/exegesis/sbl1/sbl1_v1.py
"""

import sys

from scs_analysis.cmd.cmd_gas_exegete import CmdGasExegete

from scs_core.data.json import JSONify

from scs_core.gas.exegesis.exegete_catalogue import ExegeteCatalogue
from scs_core.gas.exegesis.exegete_rendering_t_rh import ExegeteRenderingTRh


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdGasExegete()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("gas_exegete: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        exegete = ExegeteCatalogue.standard(cmd.exegete)
        available_gases = exegete.gases()

        if cmd.gas not in available_gases:
            print("gas_exegete: only gas(es) %s are supported by the exegete '%s'." % (available_gases, exegete.name()))
            exit(2)

        if cmd.verbose:
            print("gas_exegete: %s" % exegete, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        rendering = ExegeteRenderingTRh.construct(cmd.gas, cmd.rh_min, cmd.rh_max, cmd.rh_delta,
                                                  cmd.t_min, cmd.t_max, cmd.t_delta, exegete)

        for row in rendering.rows():
            print(JSONify.dumps(row.as_json()))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("gas_exegete: KeyboardInterrupt", file=sys.stderr)
