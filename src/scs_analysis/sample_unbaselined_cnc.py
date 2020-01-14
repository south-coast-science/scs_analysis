#!/usr/bin/env python3

"""
Created on 9 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_unbaselined_cnc utility is used to inject a non-baselined, simple data interpretation into any JSON document
that contains a temperature-corrected working electrode voltage (weC) field.

Simple data interpretation takes the form:

concentration [ppb] = (weC [Volts] / sensitivity [Volts / ppb]) - baseline [ppb]

The utility is intended to be used in settings where baseline offsets may have been altered over a period of time. In
this context, the baseline factor may have to be be stripped from the historic data, in order to enable a consistent
analysis. The equation applied by the sample_unbaselined_cnc utility is simply:

concentration [ppb] = weC [Volts] / sensitivity [Volts / ppb]

The user must specify the AFE serial number in order that the correct sensitivity value is used. All of the gases
specified in the calibration document are processed. The input field name for each gas is "weC". The output field name
for each gas is "u-cnc". If the output field already exists, it is overwritten.

If input values are missing or non-numeric, the input document is ignored. If any of the fields are missing, the
utility terminates.

Single sensor interface (DSI) systems are not currently supported.

NOTE: The utility requires access to the alphasense-technology web API.

SYNOPSIS
sample_unbaselined_cnc.py -a AFE_SERIAL_NUMBER [-v] REPORT_SUB_PATH

EXAMPLES
csv_reader.py gases.csv | sample_unbaselined_cnc.py -a 26-000077 val | csv_writer.py -v gases-u-cnc.csv

DOCUMENT EXAMPLE - INPUT
{"val": {"NO2": {"weV": 0.2855, "cnc": 19.4, "aeV": 0.28007, "weC": -0.00406},
"Ox": {"weV": 0.39651, "cnc": 59, "aeV": 0.38744, "weC": -0.03806},
"NO": {"weV": 0.30588, "cnc": 29.4, "aeV": 0.297, "weC": -0.04966},
"CO": {"weV": 0.34119, "cnc": 254.9, "aeV": 0.27838, "weC": 0.06405},
"sht": {"hmd": 63, "tmp": 10.7}}, "rec": "2020-01-10T13:02:38Z", "tag": "scs-bgx-401"}

DOCUMENT EXAMPLE - OUTPUT
{"val": {"NO2": {"weV": 0.2855, "cnc": 19.4, "aeV": 0.28007, "weC": -0.00406, "u-cnc": -16.6},
"Ox": {"weV": 0.39651, "cnc": 59, "aeV": 0.38744, "weC": -0.03806, "u-cnc": -85.0},
"NO": {"weV": 0.30588, "cnc": 29.4, "aeV": 0.297, "weC": -0.04966, "u-cnc": -116.6},
"CO": {"weV": 0.34119, "cnc": 254.9, "aeV": 0.27838, "weC": 0.06405, "u-cnc": 224.0},
"sht": {"hmd": 63, "tmp": 10.7}}, "rec": "2020-01-10T13:02:38Z", "tag": "scs-bgx-401"}

RESOURCES
https://www.alphasense-technology.co.uk/
https://github.com/south-coast-science/scs_core/blob/develop/src/scs_core/gas/a4/a4_temp_comp.py
https://github.com/south-coast-science/scs_dev/wiki/3:-Data-formats
"""

import sys

from collections import OrderedDict

from scs_analysis.cmd.cmd_sample_unbaselined_cnc import CmdSampleUnbaselinedCnc

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.gas.afe_calib import AFECalib

from scs_core.sys.http_exception import HTTPException

from scs_host.client.http_client import HTTPClient


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    afe_calib = None
    we_c = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleUnbaselinedCnc()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_unbaselined_cnc: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # AFECalib...
        try:
            afe_calib = AFECalib.download(HTTPClient(), cmd.afe_serial_number)

        except HTTPException as ex:
            print("sample_unbaselined_cnc: %s" % ex, file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("sample_unbaselined_cnc: %s" % afe_calib, file=sys.stderr)
            sys.stderr.flush()

        # SensorCalib lookup...
        gas_names = afe_calib.gas_names()

        sensor_calibs = OrderedDict()
        for i in range(len(afe_calib)):
            sensor_calibs[gas_names[i]] = afe_calib.sensor_calib(i)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # gases...
            for gas_name, sensor_calib in sensor_calibs.items():
                report_sub_path = cmd.report_sub_path + '.' + gas_name

                try:
                    we_c = float(datum.node(report_sub_path + '.weC'))
                except (TypeError, ValueError):
                    continue

                unbaselined_cnc = round(we_c / (sensor_calib.we_sens_mv / 1000.0), 1)
                datum.append(report_sub_path + '.u-cnc', unbaselined_cnc)

            # report...
            print(JSONify.dumps(datum))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyError as ex:
        print("sample_unbaselined_cnc: KeyError: %s" % ex, file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_unbaselined_cnc: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_unbaselined_cnc: documents: %d processed: %d" % (document_count, processed_count),
                  file=sys.stderr)
