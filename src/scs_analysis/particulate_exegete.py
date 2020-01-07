#!/usr/bin/env python3

"""
Created on 7 Jan 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The particulate_exegete utility is used to visualise the predicted scaling error of the OPC, for a given
particulates exegete and rH range.

A list of available particulates exegetes can be found using the --help flag.

SYNOPSIS
particulate_exegete.py -e EXEGETE -r RH_MIN RH_MAX RH_DELTA [-v]

EXAMPLES
particulate_exegete.py -v -e iseceen2v1 -r 10 90 5 | csv_writer.py -v iseceen2v1_rendering.csv

DOCUMENT EXAMPLE - OUTPUT
{"species": "pm1", "10 %": 0.7, "15 %": 0.8, ..., "85 %": 4.7, "90 %": 5.8}
{"species": "pm2p5", "10 %": 0.8, "15 %": 0.8, ..., "85 %": 5.3, "90 %": 6.4}
{"species": "pm10", "10 %": 0.7, "15 %": 0.7, ..., "85 %": 8.6, "90 %": 12.4}

RESOURCES
https://github.com/south-coast-science/scs_core/blob/develop/src/scs_core/particulate/exegesis/isecee/isecee_n2_v001.py

BUGS
Currently, no indication is given as to whether a particular rH value is outside the exegete's domain, and would
therefore result in a null interpretation.
"""

import sys

from scs_analysis.cmd.cmd_particulate_exegete import CmdParticulateExegete

from scs_core.data.json import JSONify

from scs_core.particulate.exegesis.exegete_catalogue import ExegeteCatalogue
from scs_core.particulate.exegesis.exegete_rendering import ExegeteRendering


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdParticulateExegete()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("particulate_exegete: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        exegete = ExegeteCatalogue.standard(cmd.exegete)

        if cmd.verbose:
            print("particulate_exegete: %s" % exegete, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        rendering = ExegeteRendering.construct(cmd.rh_min, cmd.rh_max, cmd.rh_delta, exegete)

        for row in rendering.rows():
            print(JSONify.dumps(row.as_json()))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("particulate_exegete: KeyboardInterrupt", file=sys.stderr)
