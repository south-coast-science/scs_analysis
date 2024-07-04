#!/usr/bin/env python3

"""
Created on 26 Feb 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_subset utility is used to find a subset of documents whose value for a specified field lies either
inside or outside one or two bounding values.

Input is in the form of a stream of JSON documents. Documents are written to stdout if they match the specification,
and discarded otherwise. Documents which do not have the specified field, or have an empty field value are also
discarded. If a field value is present but cannot be cast to the correct type, then the sample_subset utility
terminates.

The type of the field may be specified explicitly as either numeric or ISO 8601 datetime. If no specification is given,
the value is interpreted as a string.

Evaluation follows the rule:

lower bound <= value < upper bound

Both upper and lower bounds are optional. If both are present, then the lower bound value must be less than the upper
bound value. If neither are present, then the sample_subset utility filters out documents with missing fields or
empty values. An alternative test is --equal.

If the --exclusions flag is used, the sample_subset utility outputs only the documents that do not fit within the
specification. Note that, in this case, documents with missing or empty fields are still discarded.

SYNOPSIS
sample_subset.py { -i | -n  | -s } { [-e EQUAL] | [-l LOWER] [-u UPPER] } [-s] [-x] [-v] PATH

EXAMPLES
csv_reader.py praxis_303.csv | \
sample_subset.py -v -i -l 2018-09-26T00:00:00Z -u 2018-09-27T00:00:00Z rec

csv_reader.py -v scs-bgx-431-ref-meteo-gases-2020-H1-slp.csv | \
sample_subset.py -v "ref.NO2 Processed Measurement (ppb)" | \
csv_writer.py -v scs-bgx-431-ref-meteo-gases-2020-H1-slp-no2.csv
"""

import sys

from scs_analysis.cmd.cmd_sample_subset import CmdSampleSubset

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.datum import Datum
from scs_core.data.path_dict import PathDict

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    equal_bound = None
    lower_bound = None
    upper_bound = None
    value = None

    document_count = 0
    processed_count = 0
    output_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleSubset()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_subset (%s)' % cmd.path, verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        try:
            equal_bound = cmd.equal
        except ValueError as ex:
            logger.error("invalid value for equal: %s" % ex)
            exit(2)

        try:
            lower_bound = cmd.lower
        except ValueError as ex:
            logger.error("invalid value for lower bound: %s" % ex)
            exit(2)

        try:
            upper_bound = cmd.upper
        except ValueError as ex:
            logger.error("invalid value for upper bound: %s" % ex)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            is_member = True

            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            paths = datum.paths()

            # value...
            if cmd.path not in paths:
                continue

            value_node = datum.node(cmd.path)

            if value_node == '':
                continue

            if cmd.iso8601:
                value = LocalizedDatetime.construct_from_iso8601(value_node)

                if value is None:
                    if cmd.strict:
                        logger.error("invalid ISO 8601 value '%s' in %s" % (value_node, jstr))
                        exit(1)
                    else:
                        is_member = False

            elif cmd.numeric:
                value = Datum.float(value_node)

                if value is None:
                    if cmd.strict:
                        logger.error("invalid numeric value '%s' in %s" % (value_node, jstr))
                        exit(1)
                    else:
                        is_member = False

            else:
                value = value_node

                if value is None or value == '':
                    continue

            processed_count += 1

            # bounds...
            if lower_bound is not None or upper_bound is not None:
                try:
                    if equal_bound is not None:
                        is_member = value == equal_bound
                    else:
                        is_member = (lower_bound is None or value >= lower_bound) and \
                                    (upper_bound is None or value < upper_bound)

                except TypeError as ex:
                    if cmd.strict:
                        logger.error("TypeError: %s" % jstr)
                        exit(1)
                    else:
                        continue

            # inclusions...
            if (cmd.inclusions and not is_member) or (cmd.exclusions and is_member):
                continue

            # report...
            print(jstr)
            sys.stdout.flush()

            output_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        logger.error(repr(ex))
        exit(1)

    finally:
        logger.info("documents: %d processed: %d output: %d rejected: %d" %
                    (document_count, processed_count, output_count, document_count - output_count))
