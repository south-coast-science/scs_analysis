#!/usr/bin/env python3

"""
Created on 4 Feb 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The gas_exegesis utility is used to perform error correction on temperature-corrected gas concentrations
(reported as 'cnc') as delivered by the scs_dev/gases_sampler utility.

Input is in the form of a sequence of JSON sense documents. The output includes the original document, plus
a field containing the specified interpretation. If an interpretation with the given name already exists on the input
document, it is overwritten.

The input document must contain a temperature (t) field and relative humidity (rH) field, in addition to cnc fields
for any number of gases. Correction is performed on all of the gases supported by the selected exegete.

If the t or rH field is missing or empty, the document is ignored. If the values is malformed, or if the cnc fields
are malformed, the gas_exegesis utility terminates.

A list of available gas exegetes can be found using the --help flag. The name of the model forms the last part
of the path for its report field. For the output, the default exegesis root is "exg".

SYNOPSIS
Usage: gas_exegesis.py -e EXEGETE [-o OFFSET] [-v] RH_PATH T_PATH REPORT_SUB_PATH [EXEGESIS_ROOT]

EXAMPLES
csv_reader.py -v gases.csv | \
gas_exegesis.py -e sbl1v1 -v val.sht.hmd val.sht.tmp val | \
csv_writer.py -v gases-corrected.csv

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-bgb-410", "val": {"NO2": {"weC": -0.01333, "cnc": -3.2, "aeV": 0.29013, "weV": 0.29313},
"sht": {"tmp": 26.3, "hmd": 46.4}, "CO": {"weC": 0.21045, "cnc": 731.2, "aeV": 0.16213, "weV": 0.6132}},
"rec": "2020-02-04T16:24:16Z"}

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-bgb-410", "val": {"NO2": {"weC": -0.01333, "cnc": -3.2, "aeV": 0.29013, "weV": 0.29313},
"sht": {"tmp": 26.3, "hmd": 46.4}, "CO": {"weC": 0.21045, "cnc": 731.2, "aeV": 0.16213, "weV": 0.6132}},
"rec": "2020-02-04T16:24:16Z", "exg": {"sbl1v1": {"NO2": {"cnc": 17.0}}}}

SEE ALSO
scs_analysis/gas_exegete

RESOURCES
https://github.com/south-coast-science/scs_core/blob/develop/src/scs_core/gas/exegesis/sbl1/sbl1_v1.py
"""

import sys

from scs_analysis.cmd.cmd_gas_exegesis import CmdGasExegesis

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.gas.exegesis.exegete_catalogue import ExegeteCatalogue


# TODO: consider computing u-cnc with AFE calibration, like sample_unbaselined_cnc.py

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    rh = None
    t = None

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

        exegete_gas_names = exegete.gas_names()
        exegesis_path = '.'.join((cmd.exegesis_path, exegete.name()))


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # source...
            if cmd.rh_path not in paths or cmd.t_path not in paths or not datum.has_sub_path(cmd.report_path):
                continue

            rh_node = datum.node(cmd.rh_path)
            t_node = datum.node(cmd.t_path)
            report_node = datum.node(cmd.report_path)

            if rh_node == '' or t_node == '':
                continue

            try:
                rh = float(rh_node)
            except ValueError:
                print("gas_exegesis: invalid value for rh in %s" % jstr, file=sys.stderr)
                exit(1)

            try:
                t = float(t_node)
            except ValueError:
                print("gas_exegesis: invalid value for t in %s" % jstr, file=sys.stderr)
                exit(1)

            # correction...
            for gas_name in report_node:                            # uses source document ordering
                if gas_name not in exegete_gas_names:
                    continue

                corrected_path = '.'.join((exegesis_path, gas_name, 'cnc'))

                text = report_node[gas_name]['cnc']
                interpretation = exegete.interpretation(gas_name, text, rh, t) + cmd.offset

                datum.append(corrected_path, Datum.float(interpretation, 1))

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
            print("gas_exegesis: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
