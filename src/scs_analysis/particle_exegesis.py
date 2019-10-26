#!/usr/bin/env python3

"""
Created on 26 Oct 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The particle_exegesis utility is used to

SYNOPSIS
particle_exegesis.py -e EXEGETE [-v] RH_PATH PMX_PATH [EXEGESIS_PATH]

EXAMPLES
aws_topic_history.py org/heathrow/loc/4/particulates -t1 | particle_exegesis.py -v -e isece1 val.sht.hmd val

DOCUMENT EXAMPLE - INPUT
{"val": {"mtf1": 28, "pm1": 0.4, "mtf5": 0, "pm2p5": 0.5, "mtf3": 31, "pm10": 0.5, "mtf7": 0, "per": 4.9, "sfr": 5.2,
"sht": {"hmd": 45.6, "tmp": 20}}, "rec": "2019-10-26T16:59:02Z", "tag": "scs-bgx-431", "src": "N3"}

DOCUMENT EXAMPLE - OUTPUT
{"val": {"mtf1": 28, "pm1": 0.4, "mtf5": 0, "pm2p5": 0.5, "mtf3": 31, "pm10": 0.5, "mtf7": 0, "per": 4.9, "sfr": 5.2,
"sht": {"hmd": 45.6, "tmp": 20}}, "rec": "2019-10-26T16:59:02Z", "tag": "scs-bgx-431", "src": "N3",
"exg": {"isece1": {"pm1": 0.3, "pm2p5": 0.3, "pm10": 0.3}}}

RESOURCES
"""

import sys

from scs_analysis.cmd.cmd_particle_exegesis import CmdParticleExegesis

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.particulate.exegesis.exegete import Exegete
from scs_core.particulate.exegesis.text import Text

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    rh = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdParticleExegesis()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("particle_exegesis: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        exegete = Exegete.model(cmd.exegete, Host)

        if cmd.verbose:
            print("particle_exegesis: %s" % exegete, file=sys.stderr)
            sys.stderr.flush()

        exegesis_path = cmd.exegesis_path + '.' + exegete.name()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # sources...
            if cmd.rh_path not in paths or not datum.has_sub_path(cmd.pmx_path):
                continue

            rh_node = datum.node(cmd.rh_path)
            pmx_node = datum.node(cmd.pmx_path)

            if rh_node == '':
                continue

            try:
                rh = float(rh_node)
            except ValueError:
                print("particle_exegesis: invalid value for rh in %s" % jstr, file=sys.stderr)
                exit(1)

            # target...
            text = Text.construct_from_jdict(pmx_node)
            interpretation = exegete.interpret(text, rh)
            datum.append(exegesis_path, interpretation.as_json())

            # report...
            print(JSONify.dumps(datum))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("particle_exegesis: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("particle_exegesis: documents: %d processed: %d" % (document_count, processed_count),
                  file=sys.stderr)
