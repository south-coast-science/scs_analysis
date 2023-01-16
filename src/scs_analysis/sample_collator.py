#!/usr/bin/env python3

"""
Created on 15 Apr 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_collator utility is used to separate input JSON document dependent values according to the upper and lower
bounds of an independent value. For each column, assignment follows the rule:

lower bound <= value < upper bound

The upper and lower bounds for the data set should be specified, along with a delta size. The number of columns required
to service this domain is calculated automatically. The path identifying the leaf node in the input document for both
the independent and dependent fields must be specified.

For each input document, if either the independent or dependent variable values cannot be interpreted ans a number,
then the document is ignored. If either of the fields is not present, the sample_collator utility terminates.

Two collators are provided in this package: sample_collator collates into separate columns (collate to columns),
whereas csv_collator collates into separate CSV files (collate to rows).

SYNOPSIS
sample_collator.py -x IND_PATH [-n NAME] -y DEP_PATH [-l LOWER_BOUND] -u UPPER_BOUND -d DELTA [-v]

EXAMPLES
csv_reader.py -v -l 1 scs-pb1-3-ref-opc-r1-error-2019-09-27T11-03-41+01-00-15min-exegesis-error.csv | \
sample_collator.py -v -x "ref.pmx.PM25 Processed Measurement (µg/m³)" -y error.pm2p5 -u 60 -d 10

DOCUMENT EXAMPLE - INPUT
{"rec": "2019-10-11T10:15:00Z",
"opc": {"pmx": {"tag": "scs-pb1-3", "src": "R1", "val": {"per": 9.9, "pm1": 2.2, "pm2p5": 8.4, "pm10": 12.0}}},
"error": {"pm1": 1.517, "pm2p5": 3.561, "pm10": 3.429}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2019-10-11T10:15:00Z",
"opc": {"pmx": {"tag": "scs-pb1-3", "src": "R1", "val": {"per": 9.9, "pm1": 2.2, "pm2p5": 8.4, "pm10": 12.0}}},
"error": {"pm1": 1.517, "pm2p5": {"src": 3.561, "PM25_0-10": 3.561, "PM25_10-20": null, "PM25_20-30": null,
"PM25_30-40": null, "PM25_40-50": null, "PM25_50-60": null, "PM25_60-70": null}, "pm10": 3.429}}

SEE ALSO
scs_analysis/csv_collator
"""

import sys

from scs_analysis.cmd.cmd_sample_collator import CmdSampleCollator

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.data.sample_delta import SampleDelta


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleCollator()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_collator: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        deltas = SampleDelta.deltas(cmd.lower, cmd.upper, cmd.delta, name=cmd.name)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # collect data...
        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)
            paths = datum.paths()

            document_count += 1

            if cmd.ind_path not in paths:
                print("sample_collator: independent path not in datum: %s" % cmd.ind_path, file=sys.stderr)
                exit(1)

            try:
                ind_value = float(datum.node(cmd.ind_path))
            except ValueError:
                continue                                            # independent value is NaN - skip this row

            if cmd.dep_path not in paths:
                print("sample_collator: dependent path not in datum: %s" % cmd.dep_path, file=sys.stderr)
                exit(1)

            try:
                dep_value = float(datum.node(cmd.dep_path))
            except ValueError:
                continue                                            # dependent value is NaN - skip this row

            target = PathDict()

            for path in paths:
                if path != cmd.dep_path:
                    target.copy(datum, path)
                    continue

                target.append('.'.join((cmd.dep_path, 'src')), dep_value)

                for delta in deltas:
                    value = dep_value if delta.includes(ind_value) else None
                    target.append('.'.join((cmd.dep_path, delta.description())), value)

            print(JSONify.dumps(target))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        print("sample_collator: %s" % repr(ex), file=sys.stderr)
        exit(1)

    finally:
        if cmd.verbose:
            print("sample_collator: documents: %d processed: %d" % (document_count, processed_count), file=sys.stderr)
