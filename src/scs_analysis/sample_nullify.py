#!/usr/bin/env python3

"""
Created on 4 Sep 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_nullify utility is used to nullify values where that value - or some other value in the same JSON document -
are outside one or two bounding values. If present, values must be numeric. If not present, the JSON document is passed
to stdout without alteration.

Evaluation follows the rule:

lower bound <= value < upper bound

Both upper and lower bounds are optional. If both are present, then the lower bounding value must be less than the
upper bounding value.

SYNOPSIS
sample_nullify.py -t TARGET_PATH -s SOURCE_PATH [-l LOWER] [-u UPPER] [-v]

EXAMPLES
csv_reader.py -v scs-bgx-405-corrected-2019-04-1min.csv | sample_nullify.py -v -u 80 -s meteo.val.hmd -t proc_PM10 |
csv_writer.py -v scs-bgx-405-corrected-2019-04-1min-r80.csv

DOCUMENT EXAMPLE - INPUT
{"rec": "2019-04-27T02:07:00Z", "opc": {"tag": "scs-bgx-405", "src": "N2",
"val": {"per": 9.9, "pm1": 2.6, "pm2p5": 3.9, "pm10": 7.0}}, "meteo": {"tag": "scs-bgx-405",
"val": {"hmd": 87.6, "tmp": 20.0, "bar": ""}}, "error_model": 4.684,
"proc_PM10": 1.5, "proc_PM2p5": 0.8, "proc_PM1": 0.6}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2019-04-27T02:07:00Z", "opc": {"tag": "scs-bgx-405", "src": "N2",
"val": {"per": 9.9, "pm1": 2.6, "pm2p5": 3.9, "pm10": 7.0}}, "meteo": {"tag": "scs-bgx-405",
"val": {"hmd": 87.6, "tmp": 20.0, "bar": ""}}, "error_model": 4.684,
"proc_PM10": "", "proc_PM2p5": 0.8, "proc_PM1": 0.6}
"""

import sys

from scs_analysis.cmd.cmd_sample_nullify import CmdSampleNullify

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0
    nullified_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleNullify()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_nullify: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()
            if cmd.source not in paths or cmd.target not in paths:
                continue

            value_node = datum.node(cmd.source)

            if value_node is not None and value_node != '':
                try:
                    source_value = float(value_node)
                except ValueError:
                    source_value = None
                    print("sample_nullify: invalid numeric value '%s' in %s" % (value_node, jstr), file=sys.stderr)
                    exit(1)

                if (cmd.lower is not None and source_value < cmd.lower) or \
                        (cmd.upper is not None and source_value >= cmd.upper):
                    datum.set_node(cmd.target, None)
                    nullified_count += 1

            print(JSONify.dumps(datum))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        print("sample_nullify: %s" % repr(ex), file=sys.stderr)
        exit(1)

    finally:
        if cmd.verbose:
            print("sample_nullify: documents: %d processed: %d nullified: %d" %
                  (document_count, processed_count, nullified_count), file=sys.stderr)
