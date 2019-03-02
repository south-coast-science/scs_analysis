#!/usr/bin/env python3

"""
Created on 24 Oct 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_aggregate utility provides linear regression midpoints for data delivered on stdin, over specified units of
time. It can perform this operation for one or many nodes of the input documents.

When each time checkpoint is encountered in the input stream, the midpoint values - together with min and max, if
requested -  are computed and reported. These values are marked with the datetime indicating the end of that period.
When the input stream is closed, any remaining values are reported and marked with the next checkpoint.

Checkpoints are specified in the form HH:MM:SS, in a format similar to that for crontab:

** - all values
NN - exactly matching NN
/N - every match of N

For example, **:/5:30 indicates 30 seconds past the minute, every 5 minutes, during every hour.

Data sources are specified as a path into the input JSON document in the same format as the node command. Any number of
paths can be specified, including none (process all paths). If a path to an internal node in the JSON document is
specified, then all of the leaf-node descendants of that node will be processed.

Note that the leaf-node paths to be processed are obtained from the paths provided on the command line, and the
actual paths found in the first JSON document. Paths that do not exist in the first document are ignored.

The input JSON document must contain a field labelled 'rec', providing an ISO 8601 localised datetime. If this field
is not present then the document is skipped. Note that the timezone of the output rec datetimes is the same as the
input rec values.

If the input document does not contain a specified path - or if the value is null - then the value is ignored. Aside
from null, values must be integers or floats.

At each checkpoint, if there are no values for a given path, then only the rec field is reported. If the fill flag is
set, then any checkpoints missing in the input data are written to stdout in sequence.

SYNOPSIS
sample_aggregate.py -c HH:MM:SS [-m] [-t] [-f] [-i] [-v] [PATH_1..PATH_N]

EXAMPLES
csv_reader.py gases.csv | sample_aggregate.py -f -c **:/5:00 val
"""

import sys

from scs_analysis.cmd.cmd_sample_aggregate import CmdSampleAggregate
from scs_analysis.helper.sample_aggregate import SampleAggregate

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    aggregate = None

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleAggregate()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_aggregate: %s" % cmd, file=sys.stderr)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        generator = cmd.checkpoint_generator

        aggregate = SampleAggregate(cmd.min_max, cmd.include_tag, cmd.iso, cmd.nodes)

        if cmd.verbose:
            print("sample_aggregate: %s" % aggregate, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        checkpoint = None

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
                checkpoint = generator.enclosing_localised_datetime(rec)

            # report and reset...
            if rec.datetime > checkpoint.datetime:
                aggregate.print(checkpoint)
                aggregate.reset()

                filler = checkpoint
                checkpoint = generator.enclosing_localised_datetime(rec)

                # fill missing...
                while cmd.fill:
                    filler = generator.next_localised_datetime(filler)

                    if filler >= checkpoint:
                        break

                    aggregate.print(filler)

            # append sample...
            aggregate.append(rec, datum)

            processed_count += 1

        # report remainder...
        if aggregate.has_value():
            aggregate.print(checkpoint)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_aggregate: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            output_count = 0 if aggregate is None else aggregate.output_count

            print("sample_aggregate: documents: %d processed: %d output: %d" %
                  (document_count, processed_count, output_count), file=sys.stderr)
