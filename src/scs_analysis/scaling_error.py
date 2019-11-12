#!/usr/bin/env python3

"""
Created on 6 Nov 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The scaling_error utility may be used to determine the error in reported particulate densities from
an optical particle counter (OPC). The scaling error is simply:

error = reported_value / reference_value

Input is a sequence of JSON documents on stdin, containing both reported and reference values. If the specified
REFERENCE_PATH and REPORTED_PATH are not present, the utility terminates. If either value cannot be interpreted as a
floating-point value, the document is ignored. If the specified ERROR_PATH is already present in the document, it is
overwritten.

SYNOPSIS
scaling_error.py [-p PRECISION] [-v] REFERENCE_PATH REPORTED_PATH ERROR_PATH

EXAMPLES
csv_reader.py -v Pi-R1-joined-2019-10-15min.csv | \
scaling_error.py -v "fidas.PM25 Converted Measurement" r1.val.pm2p5 error.pm2p5 | \
scaling_error.py -v "fidas.PM10 Converted Measurement" r1.val.pm10 error.pm10 | \
csv_writer.py -v Pi-R1-joined-2019-10-15min-error.csv

DOCUMENT EXAMPLE - INPUT
{"rec": "2019-09-24T13:15:00Z", "fidas": {"Site": "Heathrow LHR2", "SiteCode": "LHR2",
"PM10 Processed Measurement": 6.3, "PM10 Converted Measurement": 6.3, "PM10 Data Status": "Provisional",
"PM25 Processed Measurement": 3.447, "PM25 Converted Measurement": 3.2519, "PM25 Data Status": "Provisional"},
"r1": {"val": {"mtf1": 32.4, "pm1": 2.1, "mtf5": 34.1, "pm2p5": 6.3, "sht": {"hmd": 29.5, "tmp": 33.0}},
"tag": "scs-pb1-3", "src": "R1"}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2019-09-24T13:15:00Z", "fidas": {"Site": "Heathrow LHR2", "SiteCode": "LHR2",
"PM10 Processed Measurement": 6.3, "PM10 Converted Measurement": 6.3, "PM10 Data Status": "Provisional",
"PM25 Processed Measurement": 3.447, "PM25 Converted Measurement": 3.2519, "PM25 Data Status": "Provisional"},
"r1": {"val": {"mtf1": 32.4, "pm1": 2.1, "mtf5": 34.1, "pm2p5": 6.3, "sht": {"hmd": 29.5, "tmp": 33.0}},
"tag": "scs-pb1-3", "src": "R1"},
"error": {"pm2p5": 1.937, "pm10": 1.889}}
"""

import sys

from scs_analysis.cmd.cmd_scaling_error import CmdScalingError

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# TODO: support both linear and scaling errors, and use this script to replace sample_error

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdScalingError()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("scaling_error: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        max_datum = None

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            document_count += 1

            # reference...
            if cmd.reference_path not in datum.paths():
                print("scaling_error: reference path '%s' not present" % cmd.reference_path, file=sys.stderr)
                exit(1)

            try:
                reference = float(datum.node(cmd.reference_path))
            except (TypeError, ValueError):
                continue

            # reported...
            if cmd.reported_path not in datum.paths():
                print("scaling_error: reported path '%s' not present" % cmd.reference_path, file=sys.stderr)
                exit(1)

            try:
                reported = float(datum.node(cmd.reported_path))
            except (TypeError, ValueError):
                continue

            # error...
            error = round(reported / reference, cmd.precision)      # TODO: / or -

            # report...
            datum.append(cmd.error_path, error)
            sys.stdout.flush()

            processed_count += 1

            print(JSONify.dumps(datum))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("scaling_error: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("scaling_error: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
