#!/usr/bin/env python3

"""
Created on 24 Oct 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_aggregate utility provides regression midpoints for data delivered on stdin, over specified units of
time, or over the entire dataset. It can perform this operation for one or many or all nodes of the input documents.

When each time checkpoint is encountered in the input stream, the midpoint values - together with min and max, if
requested -  are computed and reported. These values are marked with the datetime indicating the end of that period.
When the input stream is closed, any remaining values are reported and marked with the next checkpoint.

Checkpoints are specified in the form HH:MM:SS, in a format similar to that for Unix crontab:

** - all values
NN - exactly matching NN
/N - repeated every N

For example, **:/5:30 indicates 30 seconds past the minute, every 5 minutes, during every hour.

If no checkpoint is specified, then a single document is output - this is the aggregation of all input data.

Data sources are specified as a path into the input JSON document in the same format as the node command. Any number of
paths can be specified, including none (process all paths). If a path to an internal node in the JSON document is
specified, then all of the leaf-node descendants of that node will be processed.

Note that the leaf-node paths to be processed are obtained from the paths provided on the command line, and the
actual paths found in the first JSON document. Paths that do not exist in the first document are ignored.

The input JSON document must contain a field labelled 'rec', providing an ISO 8601 localised datetime. If this field
is not present then the document is skipped. Note that the timezone of the output rec datetimes is the same as the
input rec values. Rows with successive duplicate rec values are ignored.

Leaf node values may be numeric or strings. Numeric values are processed according to a simple linear regression.
String values are processed using a simple categorical regression.

If the input document does not contain a specified path - or if the value is null - then the value is ignored.

If a checkpoint is specified and the --exclude-remainder flag is used, then all of the input documents after the last
complete checkpoint period are ignored. Where the checkpoint is specified, a --rule flag is available. If used,
individual aggregates are rejected if less than 75% of the expected data points are present. In this case, a timedelta
must be supplied, indicating indicating the expected interval between the input samples. The interval may be found
using the aws_topic_history utility.

WARNING: The The sample_aggregate utility uses the first input document to determine the data type for the regressions.
If csv_reader is being used to supply data, then the csv_reader's --nullify flag should be used - this will prevent
numeric fields being incorrectly identified as strings.

SYNOPSIS
sample_aggregate.py [-c HH:MM:SS [-x] [-r { [DD-]HH:MM[:SS]] | :SS }]] [-m] [-i ISO] [-v] [PATH_1..PATH_N]

EXAMPLES
csv_reader.py -n gases.csv | sample_aggregate.py -v -r :10 -c **:/15:00

aws_topic_history.py -v -c super -p 00:00:00 -s 2023-12-01T00:00:00Z -e 2024-01-01T00:00:00Z \
south-coast-science-production/reference/loc/531/particulates | node.py tag rec ver src val.sfr val.sht exg | \
sample_aggregate.py | csv_writer.py -e 531-particulates-2023-12.csv
"""

import sys

from scs_analysis.cmd.cmd_sample_aggregate import CmdSampleAggregate

from scs_core.data.aggregate import Aggregate
from scs_core.data.checkpoint_generator import CheckpointGenerator
from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    rec = None
    prev_checkpoint = None
    checkpoint = None
    prev_rec = None

    document_count = 0
    processed_count = 0
    output_count = 0
    rejected_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleAggregate()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_aggregate', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)


    # ----------------------------------------------------------------------------------------------------------------
    # validation...

    if cmd.checkpoint and not CheckpointGenerator.is_valid(cmd.checkpoint):
        logger.error("the checkpoint specification %s is invalid." % cmd.checkpoint)
        exit(2)

    if not cmd.is_valid_interval():
        logger.error("invalid format for rule interval.")
        exit(2)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        generator = CheckpointGenerator.construct(cmd.checkpoint) if cmd.checkpoint else None

        aggregate = Aggregate(cmd.min_max, cmd.iso, cmd.nodes)
        logger.info(aggregate)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            # sample...
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            document_count += 1

            try:
                rec_node = datum.node(cmd.iso)
            except KeyError:
                continue

            rec = LocalizedDatetime.construct_from_iso8601(rec_node)

            # set checkpoint...
            if generator and checkpoint is None:
                prev_checkpoint = generator.prev_localised_datetime(rec)
                checkpoint = generator.next_localised_datetime(rec)

            # report and reset...
            if checkpoint and rec > checkpoint:
                if cmd.ignore_rule() or aggregate.complies_with_rule(cmd.rule_interval, checkpoint - prev_checkpoint):
                    print(JSONify.dumps(aggregate.report(checkpoint)))
                    sys.stdout.flush()
                    output_count += 1

                else:
                    rejected_count += 1

                aggregate.reset()

                if generator:
                    prev_checkpoint = checkpoint
                    checkpoint = generator.enclosing_localised_datetime(rec)

            # duplicate recs?...
            if rec == prev_rec:
                logger.info("discarding duplicate: %s" % line.strip())
                continue

            # append sample...
            aggregate.append(rec, datum)

            prev_rec = rec
            processed_count += 1

        # report remainder...
        if generator is None:
            checkpoint = rec

        if aggregate.has_value() and not cmd.exclude_remainder:
            if cmd.ignore_rule() or aggregate.complies_with_rule(cmd.rule_interval, checkpoint - prev_checkpoint):
                print(JSONify.dumps(aggregate.report(checkpoint)))
                sys.stdout.flush()
                output_count += 1

            else:
                rejected_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        logger.info("documents: %d processed: %d output: %d rejected: %d" %
                    (document_count, processed_count, output_count, rejected_count))
