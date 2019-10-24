#!/usr/bin/env python3

"""
Created on 16 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

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

import json
import sys

from scs_analysis.cmd.cmd_sample_wec_sens import CmdSampleWeCSens

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.gas.a4.a4_temp_comp import A4TempComp
from scs_core.gas.afe_calib import AFECalib
from scs_core.gas.sensor import Sensor


# TODO: cmd should specify AFE serial number and gas name

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    wec = None

    document_count = 0
    processed_count = 0

    jstr = '{"serial_number": "26-000065", "type": "810-0023", ' \
           '"calibrated_on": "2017-04-27", "dispatched_on": null, "pt1000_v20": 1.0, ' \
           '"sn1": {"serial_number": "212560021", "sensor_type": "NOGA4", ' \
           '"we_electronic_zero_mv": 289, "we_sensor_zero_mv": -3, "we_total_zero_mv": 286, ' \
           '"ae_electronic_zero_mv": 294, "ae_sensor_zero_mv": 1, "ae_total_zero_mv": 295, ' \
           '"we_sensitivity_na_ppb": -0.398, "we_cross_sensitivity_no2_na_ppb": -0.398, "pcb_gain": -0.73, ' \
           '"we_sensitivity_mv_ppb": 0.29, "we_cross_sensitivity_no2_mv_ppb": 0.29}, ' \
           '"sn2": {"serial_number": "214690115", "sensor_type": "OXGA4", ' \
           '"we_electronic_zero_mv": 392, "we_sensor_zero_mv": -2, "we_total_zero_mv": 390, ' \
           '"ae_electronic_zero_mv": 422, "ae_sensor_zero_mv": 0, "ae_total_zero_mv": 422, ' \
           '"we_sensitivity_na_ppb": -0.486, "we_cross_sensitivity_no2_na_ppb": -0.377, "pcb_gain": -0.73, ' \
           '"we_sensitivity_mv_ppb": 0.354, "we_cross_sensitivity_no2_mv_ppb": 0.275}, ' \
           '"sn3": {"serial_number": "130560007", "sensor_type": "NO A4", ' \
           '"we_electronic_zero_mv": 290, "we_sensor_zero_mv": 27, "we_total_zero_mv": 317, ' \
           '"ae_electronic_zero_mv": 298, "ae_sensor_zero_mv": 34, "ae_total_zero_mv": 332, ' \
           '"we_sensitivity_na_ppb": 0.506, "we_cross_sensitivity_no2_na_ppb": "n/a", "pcb_gain": 0.8, ' \
           '"we_sensitivity_mv_ppb": 0.404, "we_cross_sensitivity_no2_mv_ppb": "n/a"}, ' \
           '"sn4": {"serial_number": "132930016", "sensor_type": "CO A4", ' \
           '"we_electronic_zero_mv": 291, "we_sensor_zero_mv": 13, "we_total_zero_mv": 304, ' \
           '"ae_electronic_zero_mv": 275, "ae_sensor_zero_mv": 21, "ae_total_zero_mv": 296, ' \
           '"we_sensitivity_na_ppb": 0.294, "we_cross_sensitivity_no2_na_ppb": "n/a", "pcb_gain": 0.8, ' \
           '"we_sensitivity_mv_ppb": 0.235, "we_cross_sensitivity_no2_mv_ppb": "n/a"}}'


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

        t_path = cmd.t_path     # 'climate.val.tmp_p190'

        we_v_path = cmd.report_sub_path + '.weV'
        ae_v_path = cmd.report_sub_path + '.aeV'

        we_c_path = cmd.report_sub_path + '.weC'
        we_c_sens_path = cmd.report_sub_path + '.weC_sens'

        afe_calib = AFECalib.construct_from_jdict(json.loads(jstr))

        if cmd.verbose:
            print("sample_wec_sens: %s" % afe_calib, file=sys.stderr)

        index = afe_calib.sensor_index('NO2')
        calib = afe_calib.sensor_calib(index)

        we_sens_mv = calib.we_sens_mv

        print("we_sens_mv: %s" % we_sens_mv)

        tc = A4TempComp.find(Sensor.CODE_NO2)

        if cmd.verbose:
            print("sample_wec_sens: %s" % tc, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            t_node = datum.node(t_path)
            t = float(t_node)

            we_v_node = datum.node(we_v_path)
            we_v = float(we_v_node)

            ae_v_node = datum.node(ae_v_path)
            ae_v = float(ae_v_node)

            print("t: %s we_v: %s ae_v: %s " % (t, we_v, ae_v))

            we_t = we_v - (calib.we_elc_mv / 1000.0)  # remove electronic we zero
            ae_t = ae_v - (calib.ae_elc_mv / 1000.0)  # remove electronic ae zero

            we_c = tc.correct(calib, t, we_t, ae_t)
            we_c_sens = round(we_c / (we_sens_mv / 1000.0), 1)

            print("we_c: %s we_c_sens: %s" % (we_c, we_c_sens))

            # copy...
            target = PathDict()

            for path in paths:
                if path == we_c_sens_path:
                    continue                                        # ignore any existing wec_sens_path

                target.append(path, datum.node(path))

                if path == we_c_path:
                    target.append(we_c_sens_path, we_c_sens)

            # report...
            print(JSONify.dumps(target.node()))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_wec_sens: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_wec_sens: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
