#!/usr/bin/env python3

"""
Created on 19 Jun 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_mdape utility is used to compute Median Absolute Percent Error (MdAPE). Output is in the form of either a
scalar MdAPE value, or an array of data points.

If the --errors flag is set, then the utility outputs an array of JSON documents specifying the reference, prediction
and error value for each input document. Otherwise, the utility reports the computed MdAPE value.

SYNOPSIS
sample_mdape.py [-p PRECISION] [-e] [-v] REFERENCE_PATH PREDICTION_PATH

EXAMPLES - MdAPE
csv_reader.py -v ref-scs-opc-mash-meteo-pmx-Y22-15min-slope-pm1-clean-validation-vB-xm-exg.csv | \
sample_mdape.py -v src.ref.PM1 exg.PM1.vB.opc-mash.Y22

EXAMPLES - ERRORS
csv_reader.py -v ref-scs-opc-mash-meteo-pmx-Y22-15min-slope-pm1-clean-validation-vB-xm-exg.csv | \
sample_mdape.py -e -v src.ref.PM1 exg.PM1.vB.opc-mash.Y22 | \
histo_chart.py -vb -x 0 100 -c 100 ape

DOCUMENT EXAMPLE - ERRORS OUTPUT
[{"src.ref.PM1": 2.47, "exg.PM1.vB.opc-mash.Y22": 2.7, "ape": 9.312}, ...]

RESOURCES
MdAPE - Median Absolute Percentage Error
https://support.numxl.com/hc/en-us/articles/115001223503-MdAPE-Median-Absolute-Percentage-Error
"""

import json
import sys

from scs_analysis.cmd.cmd_sample_mdape import CmdSampleMdAPE

from scs_core.data.mdape import MdAPE
from scs_core.data.path_dict import PathDict

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

def node(path):
    try:
        return float(datum.node(path))

    except KeyError:
        logger.error("missing value for '%s': %s" % (path, line.strip()))
        exit(1)

    except ValueError:
        logger.error("invalid value for '%s': %s" % (path, line.strip()))
        exit(1)

    except TypeError:
        return None


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleMdAPE()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_mdape', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        sampler = MdAPE(precision=cmd.precision)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        errors = []

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            document_count += 1

            reference = node(cmd.reference_path)

            if reference is None:
                continue

            prediction = node(cmd.prediction_path)

            if prediction is None:
                continue

            ape = sampler.append(reference, prediction)

            if cmd.errors:
                print(json.dumps({cmd.reference_path: reference, cmd.prediction_path: prediction, 'ape': ape}))

            processed_count += 1

        if not cmd.errors:
            print(sampler.mdape())


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        logger.info("documents: %d processed: %d" % (document_count, processed_count))
