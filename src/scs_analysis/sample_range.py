#!/usr/bin/env python3

"""
Created on 20 Jun 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_range utility is used to add full range (max - min) and upper rage (max - mid) fields to the output
documents - this is useful when analysing device outputs for correct zero offset and sensitivity.

The SUB_NODE argument indicates which input field(s) should be processed. In order to be processed the field must
contain the SUB_NODE and have contiguous leaf nodes ending '.min', '.mid' and '.max'. Fields that do not meet this
requirement are passed to the output with no additional '.full-range' and '.upper-range' fields.

SYNOPSIS
sample_range.py [-f] [-u] [-p PRECISION] [-v] SUB_NODE

EXAMPLES
sample_range.py -f -u CO.cnc

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-bgx-619", "rec": "2024-06-20T00:00:00Z",
"val": {"CO": {"cnc": {"min": 104.2, "mid": 181.8, "max": 520.7}}}}

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-bgx-619", "rec": "2024-06-20T00:00:00Z",
"val": {"CO": {"cnc": {"min": 104.2, "mid": 181.8, "max": 520.7, "full-range": 416.5, "upper-range": 338.9}}}}

SEE ALSO
scs_analysis/gas_response_summary
"""

import sys

from scs_analysis.cmd.cmd_sample_range import CmdSampleRange

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict
from scs_core.data.range import Range

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleRange()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_range', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)
            sample_range = Range(precision=cmd.precision)
            target = PathDict()

            if datum is None:
                continue

            document_count += 1

            for path in datum.paths():
                if cmd.sub_node not in path:
                    target.append(path, datum.node(path))
                    continue

                sample_range.append(path, datum.node(path))
                target.append(path, datum.node(path))

                if sample_range.is_complete():
                    if cmd.full:
                        target.append(*sample_range.full_range())

                    if cmd.upper:
                        target.append(*sample_range.upper_range())

                    sample_range.reset()

            print(JSONify.dumps(target))

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)

    finally:
        logger.info("documents: %d processed: %d" % (document_count, processed_count))
