#!/usr/bin/env python3

"""
Created on 24 Oct 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_aggregate utility provides regression midpoints for data delivered on stdin, over specified units of
time. It can perform this operation for one or many nodes of the input documents.

When each time checkpoint is encountered in the input stream, the midpoint values - together with min and max, if
requested -  are computed and reported. These values are marked with the datetime indicating the end of that period.
When the input stream is closed, any remaining values are reported and marked with the next checkpoint.

Checkpoints are specified in the form HH:MM:SS, in a format similar to that for crontab:

** - all values
NN - exactly matching NN
/N - repeated every N

For example, **:/5:30 indicates 30 seconds past the minute, every 5 minutes, during every hour.

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

A --rule flag is available. If used, individual aggregates are rejected if less than 75% of the expected data points
are present. In this case, a timedelta must be supplied, indicating indicating the expected interval between the
input samples. The interval may be found using the aws_topic_history utility.

If the --exclude-remainder flag is used, then all of the input documents after the last complete checkpoint period
are ignored.

WARNING: The The sample_aggregate utility uses the first input document to determine the data type for the regressions.
If csv_reader is being used to supply data, then the csv_reader's --nullify flag should be used - this will prevent
numeric fields being incorrectly identified as strings.

SYNOPSIS
sample_aggregate.py -c HH:MM:SS [-m] [-i ISO] [-r { [DD-]HH:MM[:SS] | :SS }] [-x] [-v] [PATH_1 .. PATH_N]

EXAMPLES
csv_reader.py -n gases.csv | sample_aggregate.py -v -r :10 -c **:/15:00
"""

import sys

from scs_analysis.cmd.cmd_sample_aggregate import CmdSampleAggregate

from scs_core.data.aggregate import Aggregate
from scs_core.data.checkpoint_generator import CheckpointGenerator
from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    prev_checkpoint = None
    checkpoint = None
    prev_rec = None
    aggregate = None

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

    if not CheckpointGenerator.is_valid(cmd.checkpoint):
        print("sample_aggregate: the checkpoint specification %s is invalid." % cmd.checkpoint, file=sys.stderr)
        exit(2)

    if not cmd.is_valid_interval():
        print("sample_aggregate: invalid format for rule interval.", file=sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_aggregate: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        generator = CheckpointGenerator.construct(cmd.checkpoint)

        aggregate = Aggregate(cmd.min_max, cmd.iso, cmd.nodes)

        if cmd.verbose:
            print("sample_aggregate: %s" % aggregate, file=sys.stderr)
            sys.stderr.flush()


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
            if checkpoint is None:
                prev_checkpoint = generator.prev_localised_datetime(rec)
                checkpoint = generator.next_localised_datetime(rec)

            # report and reset...
            if rec > checkpoint:
                if cmd.ignore_rule() or aggregate.complies_with_rule(cmd.interval, checkpoint - prev_checkpoint):
                    print(JSONify.dumps(aggregate.report(checkpoint)))
                    sys.stdout.flush()
                    output_count += 1

                else:
                    rejected_count += 1

                aggregate.reset()

                prev_checkpoint = checkpoint
                checkpoint = generator.enclosing_localised_datetime(rec)

            # duplicate recs?...
            if rec == prev_rec:
                if cmd.verbose:
                    print("sample_aggregate: discarding duplicate: %s" % line.strip(), file=sys.stderr)
                    sys.stderr.flush()

                continue

            # append sample...
            aggregate.append(rec, datum)

            prev_rec = rec
            processed_count += 1

        # report remainder...
        if aggregate.has_value() and not cmd.exclude_remainder:
            if cmd.ignore_rule() or aggregate.complies_with_rule(cmd.interval, checkpoint - prev_checkpoint):
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
        if cmd.verbose:
            print("sample_aggregate: documents: %d processed: %d output: %d rejected: %d" %
                  (document_count, processed_count, output_count, rejected_count), file=sys.stderr)
