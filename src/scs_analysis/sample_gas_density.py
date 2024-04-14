#!/usr/bin/env python3

"""
Created on 17 Jul 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_gas_density utility is used to

SYNOPSIS
sample_gas_density.py [-p PRECISION] [-v] PATH

EXAMPLES
aws_topic_history.py -vl south-coast-science-demo/brighton-urban/loc/1/gases | sample_gas_density.py -v exg.val

DOCUMENT EXAMPLE - INPUT
{... ,
"exg": {"val": {"NO2": {"cnc": 15.2}, "NO": {"cnc": 11.9}, "SO2": {"cnc": 1.1}},
"src": "uE.1"}}

DOCUMENT EXAMPLE - OUTPUT
{... ,
"exg": {"val": {"NO2": {"cnc": 15.2, "dns": 29.1}, "NO": {"cnc": 11.9, "dns": 15.9}, "SO2": {"cnc": 1.1, "dns": 2.9}},
"src": "uE.1"}}
"""

import sys

from scs_analysis.cmd.cmd_sample_gas_density import CmdSampleGasDensity

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.gas.gas import Gas

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

def gas_name(path):
    pieces = path.split('.')
    return pieces[-2]


def is_concentration(path):
    pieces = path.split('.')
    return pieces[-1] == 'cnc'


def density_path(path):
    pieces = path.split('.')
    pieces[-1] = 'dns'

    return '.'.join(pieces)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleGasDensity()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_gas_density', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        max_datum = None

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            document_count += 1

            value_paths = datum.paths(sub_path=cmd.path)

            for value_path in value_paths:
                if not is_concentration(value_path):
                    continue

                try:
                    concentration = float(datum.node(sub_path=value_path))
                except (TypeError, ValueError):
                    logger.error("invalid value for %s concentration in %s" % (gas_name(value_path), line.strip()))
                    exit(1)

                try:
                    density = Gas.density_stp(gas_name(value_path), concentration)
                except ValueError:
                    logger.error("unrecognised gas '%s' in %s" % (gas_name(value_path), line.strip()))
                    exit(1)

                datum.append(density_path(value_path), round(density, cmd.precision))

            # report...
            print(JSONify.dumps(datum))

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        logger.error(repr(ex))
        exit(1)

    finally:
        logger.info("documents: %d processed: %d" % (document_count, processed_count))
