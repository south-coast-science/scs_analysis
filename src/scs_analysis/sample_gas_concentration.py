#!/usr/bin/env python3

"""
Created on 15 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_gas_concentration utility is used to inject a gas concentration value, based on a given density (microgrammes
per cubic metre), temperature and pressure. The reported value is in parts per billion.

Density and temperature must be supplied from the input JSON document. Atmospheric pressure may be supplied from the
input JSON document. Alternatively, a pressure estimate may be supplied on the command line. In both cases, pressure
should be indicated in kilopascals (kPa). If no pressure value is supplied, the standard pressure of 101.3 kPa is used.

The path for the node in the output document indicating concentration is based on the path for the node in the
input document indicating density. For example, if the input path is SUB-PATH.dns, the output path is SUB-PATH.cnc. If
a SUB-PATH.cnc field exists in the input document, it is overwritten.

SYNOPSIS
sample_gas_concentration.py [-v] GAS DENSITY_PATH T_PATH [{P_PATH | -p PRESSURE}]

EXAMPLES
csv_reader.py joined_2019-02.csv | sample_gas_concentration.py -v NO2 ref.val.NO2.dns praxis.val.sht.tmp

DOCUMENT EXAMPLE - INPUT
{"rec": "2019-02-12T13:00:00Z", "praxis": {"val":
{"NO2": {"weV": 0.300059, "cnc": 23.4, "aeV": 0.302339, "weC": -0.002793},
"sht": {"hmd": 67.6, "tmp": 13.1}}}, "ref": {"val": {"NO2": {"units": "ugm-3", "dns": 51}}}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2019-02-12T13:00:00Z", "praxis": {"val":
{"NO2": {"weV": 0.300059, "cnc": 23.4, "aeV": 0.302339, "weC": -0.002793},
"sht": {"hmd": 67.6, "tmp": 13.1}}}, "ref": {"val": {"NO2": {"units": "ugm-3", "dns": 51, "cnc": 26.0}}}}

RESOURCES
http://www.apis.ac.uk/unit-conversion
"""

import sys

from scs_analysis.cmd.cmd_sample_gas_concentration import CmdSampleGasConcentration

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.gas.gas import Gas

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    density = None
    t = None
    p = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleGasConcentration()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_gas_concentration', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # validation...

        if not Gas.is_valid_name(cmd.gas):
            logger.error("the gas '%s' is not recognised." % cmd.gas)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        density_nodes = cmd.density_path.split('.')
        concentration_path = '.'.join(density_nodes[:-1] + ['cnc'])


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
                logger.error("invalid value for density in %s" % jstr)
                exit(1)

            try:
                t = float(t_node)
            except ValueError:
                logger.error("invalid value for t in %s" % jstr)
                exit(1)

            # p...
            if cmd.p_path:
                p_node = datum.node(cmd.p_path)

                if p_node == '':
                    continue

                try:
                    p = float(p_node)
                except ValueError:
                    logger.error("invalid value for p in %s" % jstr)
                    exit(1)

            else:
                p = cmd.pressure

            # compute...
            cnc = round(Gas.concentration(cmd.gas, density, t, p), 1)

            # copy...
            target = PathDict()

            for path in paths:
                if path == concentration_path:
                    continue

                target.append(path, datum.node(path))

                if path == cmd.density_path:
                    target.append(concentration_path, cnc)

            # report...
            print(JSONify.dumps(target))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        logger.error(repr(ex))
        exit(1)

    finally:
        logger.info("sample_gas_concentration: documents: %d processed: %d" % (document_count, processed_count))
