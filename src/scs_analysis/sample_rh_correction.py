#!/usr/bin/env python3

"""
Created on 1 Apr 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
Important note: the equation applied by this utility is experimental.

The sample_rh_correction utility is used to perform data interpretation for electrochemical sensors, taking into
account the absolute humidity (aH) at the time of the sensing operation.

The conventional equation finding gas concentration is:

concentration = (weC / sensitivity) - baseline_offset

where weC is the temperature-corrected working electrode voltage of the electrochemical sensor.

The equation used by the sample_rh_correction utility is:

corrected_sensitivity = (1 + (aH * wS)) * sensitivity
corrected_baseline_offset = (aH * wB) + baseline_offset
corrected_concentration = (weC / corrected_sensitivity) - corrected_baseline_offset

with the following weightings, indicating:

* wS - the impact of aH on the sensitivity of the sensor
* wB - the impact of aH on the baseline offset of the sensor

wS and wB should be found experimentally.

weC must be presented as a voltage, and aH as grammes / cubic metre. The corrected cnc value is in parts per billion.
If fields are missing from the input document, then the document is ignored. If values are
malformed, execution will terminate.

SYNOPSIS
sample_rh_correction.py -s SENS_MV BASELINE -c WS WB [-v] GAS_SUB_PATH AH_PATH

EXAMPLES
csv_reader.py brighton_gases-24h-1min-ah.csv | sample_rh_correction.py -s 0.295 0 -c 0 -10 -v val.NO2 val.sht.hmd.aH
csv_reader.py brighton_gases-24h-1min-ah.csv | sample_rh_correction.py -s 0.325 0 -c 1 -20 -v val.NO val.sht.hmd.aH

DOCUMENT EXAMPLE - INPUT
{"rec": "2019-04-01T00:01:00Z", "val": {
"NO2": {"cnc": 42.2, "weV": 0.287254, "aeV": 0.279535, "weC": -0.001431},
"sht": {"hmd": {"rH": 69.6, "aH": 6.7}, "tmp": 10.4}}, "tag": "scs-bgx-401"}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2019-04-01T00:01:00Z", "val": {
"NO2": {"cnc": 42.2, "cnc-ah-corr": 62.1, "weV": 0.287254, "aeV": 0.279535, "weC": -0.001431},
"sht": {"hmd": {"rH": 69.6, "aH": 6.7}, "tmp": 10.4}}, "tag": "scs-bgx-401"}

RESOURCES
https://github.com/south-coast-science/scs_dev/wiki/3:-Data-formats
"""

import sys

from scs_analysis.cmd.cmd_sample_ah_correction import CmdSampleAhCorrection

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.gas.ah_correction import AhCorrection


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleAhCorrection()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_rh_correction: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        correction = AhCorrection.construct(cmd.sens_mv, cmd.baseline_offset, cmd.ws, cmd.wb)

        if cmd.verbose:
            print("sample_rh_correction: %s" % correction, file=sys.stderr)
            sys.stderr.flush()

        # we_c_path = cmd.gas_sub_path + '.weC'
        t_path = 'praxis.val.sht.tmp'
        cnc_path = cmd.gas_sub_path + '.cnc'
        cnc_corr_path = cmd.gas_sub_path + '.cnc-rh-corr'
        cnc_t_corr_path = cmd.gas_sub_path + '.cnc-t-corr'


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # weC, aH...
            if cnc_path not in paths or cmd.ah_path not in paths:       # we_c_path
                continue

            # we_c_node = datum.node(we_c_path)
            t_node = datum.node(t_path)
            cnc_node = datum.node(cnc_path)
            rh_node = datum.node(cmd.ah_path)

            if cnc_node == '' or rh_node == '':
                continue

            try:
                cnc = float(cnc_node)
            except ValueError:
                cnc = None
                print("sample_rh_correction: invalid value for weC in %s" % jstr, file=sys.stderr)
                exit(1)

            try:
                rh = float(rh_node)
            except ValueError:
                rh = None
                print("sample_rh_correction: invalid value for aH in %s" % jstr, file=sys.stderr)
                exit(1)

            try:
                t = float(t_node)
            except ValueError:
                t = None
                print("sample_rh_correction: invalid value for t in %s" % jstr, file=sys.stderr)
                exit(1)

            # compute...
            t_comp_cnc, m_rh, c_rh, cnc_corr = correction.rh_corr(cnc, rh, t)

            # copy...
            target = PathDict()

            for path in paths:
                target.append(path, datum.node(path))

                if path == cnc_path:
                    target.append(cmd.gas_sub_path + '.m_rh', round(m_rh, 3))
                    target.append(cmd.gas_sub_path + '.c_rh', round(c_rh, 3))
                    target.append(cnc_t_corr_path, round(t_comp_cnc, 1))
                    target.append(cnc_corr_path, round(cnc_corr, 1))

            # report...
            print(JSONify.dumps(target.node()))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_rh_correction: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_rh_correction: documents: %d processed: %d" % (document_count, processed_count),
                  file=sys.stderr)
