#!/usr/bin/env python3

"""
Created on 16 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_wec_sens utility is used to inject a non-baselined, simple data interpretation into any JSON document that
contains a temperature-corrected working electrode voltage (weC) field.

Simple data interpretation takes the form:

concentration [ppb] = (weC [Volts] / sensitivity [Volts / ppb]) - baseline [ppb]

The utility is intended to be used in settings where baseline offsets may have been altered over a period of time. In
this context, the baseline factor should be stripped from the historic data, enabling a consistent analysis. The
equation applies by the sample_wec_sens utility is simply:

concentration [ppb] = weC [Volts] / sensitivity [Volts / ppb]

The appropriate gas is specified in a form such as val.NO2 - in this case, the field val.NO2.weC is read, and the field
val.NO2.weC_sens is injected into the output document. The sensitivity [mV / ppb] should be provided on the
command line. The value is normally found from the calibration sheet for the sensor.

If fields are missing from the input document, then the document is ignored. If values are
malformed, execution will terminate.

SYNOPSIS
sample_wec_sens.py -s SENS PATH [-v]

EXAMPLES
csv_reader.py gases.csv | sample_wec_sens.py -s 0.255 val.NO2

DOCUMENT EXAMPLE - INPUT
{"val": {"NO2": {"weV": 0.315317, "cnc": 21.4, "aeV": 0.309942, "weC": 0.002767},
"sht": {"hmd": 51.9, "tmp": 22.8}, "rec": "2019-02-18T14:37:07Z", "tag": "scs-be2-2"}

DOCUMENT EXAMPLE - OUTPUT
{"val": {"NO2": {"weV": 0.315317, "cnc": 21.4, "aeV": 0.309942, "weC": 0.002767, "weC_sens": 10.9},
"sht": {"hmd": 51.9, "tmp": 22.8}, "rec": "2019-02-18T14:37:07Z", "tag": "scs-be2-2"}

RESOURCES
https://github.com/south-coast-science/scs_dev/wiki/3:-Data-formats
"""

import sys

from scs_analysis.cmd.cmd_sample_wec_sens import CmdSampleWeCSens

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    wec = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleWeCSens()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_wec_sens: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        wec_path = cmd.path + '.weC'
        wec_sens_path = cmd.path + '.weC_sens'


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            paths = datum.paths()

            # weC...
            if wec_path not in paths:
                continue

            wec_node = datum.node(wec_path)

            if wec_node == '':
                continue

            try:
                wec = float(wec_node)
            except ValueError:
                print("sample_wec_sens: invalid value for %s in %s" % (wec_path, jstr), file=sys.stderr)
                exit(1)

            wec_sens = round(wec / (cmd.sens / 1000), 1)

            target = PathDict()

            # copy...
            for path in paths:
                if path == wec_sens_path:
                    continue                                        # ignore any existing wec_sens_path

                if path == wec_path:
                    target.append(wec_path, wec)
                    target.append(wec_sens_path, wec_sens)

                else:
                    target.append(path, datum.node(path))

            # report...
            print(JSONify.dumps(target.node()))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_wec_sens: KeyboardInterrupt", file=sys.stderr)
