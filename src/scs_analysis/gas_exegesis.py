#!/usr/bin/env python3

"""
Created on 26 Oct 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The gas_exegesis utility is used to perform data interpretation on

Input is in the form of a sequence of JSON sense documents. The output includes the original document, plus
a field containing the specified interpretation. If an interpretation with the given name already exists on the input
document, it is overwritten.

The input document must contain a relative humidity (rH) field, in addition to pm1, pm2p5.5 and pm10 fields. If the rH
field is missing or empty, the document is ignored. If the rH value is malformed, or if the PM fields are missing
or malformed, the gas_exegesis utility terminates.

A list of available particulates exegetes can be found using the --help flag. The name of the model forms the last part
of the path for its report field. For the output, the default exegesis root is "exg".

SYNOPSIS
gas_exegesis.py -e EXEGETE [-v] RH_PATH PMX_PATH [EXEGESIS_PATH]

EXAMPLES
csv_reader.py -v preston-circus-2020-01-07-joined.csv | \
gas_exegesis.py -v -e iselutn2v1 meteo.val.hmd opc.val opc | \
csv_writer.py -v preston-circus-2020-01-07-exg.csv

DOCUMENT EXAMPLE - INPUT
{"val": {"mtf1": 28, "pm1": 0.4, "mtf5": 0, "pm2p5": 0.5, "mtf3": 31, "pm10": 0.5, "mtf7": 0, "per": 4.9, "sfr": 5.2,
"sht": {"hmd": 45.6, "tmp": 20}}, "rec": "2019-10-26T16:59:02Z", "tag": "scs-bgx-431", "src": "N3"}

DOCUMENT EXAMPLE - OUTPUT
{"val": {"mtf1": 27, "pm1": 1.9, "mtf5": 34, "pm2p5": 2.5,  "mtf3": 30, "pm10": 2.6, "mtf7": 0, "per": 4.9, "sfr": 5.81,
"sht": {"hmd": 46.6, "tmp": 18}}, "rec": "2019-10-26T19:56:32Z", "tag": "scs-bgx-431", "src": "N3",
"exg": {"isecen2v1": {"pm1": 1.2, "pm2p5": 1.6, "pm10": 1.7}}}

RESOURCES
https://github.com/south-coast-science/scs_core/blob/develop/src/scs_core/particulate/exegesis/isecee/isecee_n2_v001.py
"""

import sys

from scs_analysis.cmd.cmd_gas_exegesis import CmdGasExegesis

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.gas.exegesis.exegete_catalogue import ExegeteCatalogue
# from scs_core.gas.exegesis.text import Text


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    t = None
    rh = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdGasExegesis()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("gas_exegesis: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        exegete = ExegeteCatalogue.standard(cmd.exegete)

        if cmd.verbose:
            print("gas_exegesis: %s" % exegete, file=sys.stderr)
            sys.stderr.flush()

        exegesis_path = cmd.exegesis_path + '.' + exegete.name()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        exit(0)

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # source...
            if cmd.t_path not in paths or cmd.rh_path not in paths or not datum.has_sub_path(cmd.report_path):
                continue

            t_node = datum.node(cmd.t_path)
            rh_node = datum.node(cmd.rh_path)
            report_node = datum.node(cmd.report_path)

            if t_node == '' or rh_node == '':
                continue

            try:
                t = float(t_node)
            except ValueError:
                print("gas_exegesis: invalid value for t in %s" % jstr, file=sys.stderr)
                exit(1)

            try:
                rh = float(rh_node)
            except ValueError:
                print("gas_exegesis: invalid value for rh in %s" % jstr, file=sys.stderr)
                exit(1)

            # interpretation...
            # text = Text.construct_from_jdict(report_node)
            interpretation = exegete.interpretation(None, t, rh)             # text
            datum.append(exegesis_path, interpretation.as_json())

            # report...
            print(JSONify.dumps(datum))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyError as ex:
        print("gas_exegesis: KeyError: %s" % ex, file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("gas_exegesis: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("gas_exegesis: documents: %d processed: %d" % (document_count, processed_count),
                  file=sys.stderr)
