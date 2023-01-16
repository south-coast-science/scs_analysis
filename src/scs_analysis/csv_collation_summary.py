#!/usr/bin/env python3

"""
Created on 2 Nov 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The csv_collation_summary utility is used alongside csv_collator to report on the effect of one independent variable
on one or more dependent variables, for a range of independent variable deltas.

Input is gained from a sequence of CSV files, as created by the csv_collator utility. Input rows with missing or
malformed values for any of the variables are ignored. If the specified columns for any of the named variables
are missing, the utility terminates.

The output of csv_collation_summary is a sequence of JSON documents, detailing the min, median and max values for the
independent variable, with the median and standard deviation of each of the dependent variables.

If the --verbose flag is used, a summary of the data processed is written to stderr.

SYNOPSIS
csv_collation_summary.py  -f FILE_PREFIX -i IND_PATH [-p IND_PRECISION DEP_PRECISION] [-v] DEP_PATH_1 .. DEP_PATH_N

EXAMPLES
csv_collation_summary.py -v -f collated_5rH/joined_PM_meteo_data_2019-02_2019-07_15min_ \
-i th.praxis.val.hmd pm1_scaling pm2p5_scaling pm10_scaling | \
csv_writer.py -v collated_5rH/summary.csv

FILES
Input file names must be of the form:
FILE-PREFIX_DOMAIN-LOW_DOMAIN-HIGH.csv

DOCUMENT EXAMPLE - OUTPUT
{"domain": "70.0 - 75.0", "praxis": {"climate": {"val": {"hmd": {"min": 70.0, "avg": 72.6, "max": 74.9}}}},
"error": {"pm1": {"avg": 2.648, "stdev": 2.458}, "pm2p5": {"avg": 2.992, "stdev": 2.652},
"pm10": {"avg": 2.77, "stdev": 2.456}}, "samples": 2307}

SEE ALSO
scs_analysis/csv_collator

RESOURCES
https://en.wikipedia.org/wiki/Dependent_and_independent_variables
"""

import sys

from scs_analysis.cmd.cmd_csv_collation_summary import CmdCollationSummary
from scs_analysis.handler.csv_collator import CSVCollatorBin

from scs_core.csv.csv_reader import CSVReader, CSVReaderException

from scs_core.data.json import JSONify
from scs_core.data.model_delta import ModelDelta
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    file_count = 0
    total_rows = 0
    total_processed = 0

    reader = None
    domain = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdCollationSummary()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("csv_collation_summary: %s" % cmd, file=sys.stderr)

    try:
        for filename in cmd.filenames:

            file_count += 1
            rows = 0
            processed = 0

            # --------------------------------------------------------------------------------------------------------
            # resources...

            try:
                domain_min, domain_max = CSVCollatorBin.parse(filename)
            except ValueError:
                print("csv_collation_summary: skipping file: %s" % filename, file=sys.stderr)
                sys.stderr.flush()
                continue

            try:
                reader = CSVReader.construct_for_file(filename)
            except FileNotFoundError:
                print("csv_collation_summary: file not found: %s" % filename, file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print("csv_collation_summary: %s" % filename, file=sys.stderr)
                sys.stderr.flush()


            # --------------------------------------------------------------------------------------------------------
            # run...

            delta = ModelDelta.construct(domain_min, domain_max, cmd.ind_path, cmd.ind_prec, cmd.dep_paths,
                                         cmd.dep_prec)

            try:
                for row in reader.rows():
                    datum = PathDict.construct_from_jstr(row)
                    paths = datum.paths()

                    rows += 1

                    if cmd.ind_path not in paths:
                        print("csv_collation_summary: ind_path not in datum: %s" % cmd.ind_path, file=sys.stderr)
                        exit(1)

                    try:
                        ind_value = float(datum.node(cmd.ind_path))
                    except ValueError:
                        continue                        # independent value is NaN - skip this row

                    dependents = {}
                    for dep_path in cmd.dep_paths:
                        if dep_path not in paths:
                            print("csv_collation_summary: dep_path not in datum: %s" % dep_path, file=sys.stderr)
                            exit(1)

                        try:
                            dep_value = float(datum.node(dep_path))
                        except ValueError:
                            break

                        dependents[dep_path] = dep_value

                    try:
                        delta.append(ind_value, dependents)
                    except IndexError:
                        continue                        # at least one dependent value is NaN - skip this row

                    processed += 1

            except CSVReaderException as ex:
                if cmd.verbose:
                    print("csv_collation_summary: terminating: %s" % ex, file=sys.stderr)
                    exit(1)

            finally:
                if reader is not None:
                    reader.close()

            print(JSONify.dumps(delta))
            sys.stdout.flush()

            if cmd.verbose:
                print("csv_collation_summary: rows: %d processed: %d" % (rows, processed), file=sys.stderr)

            total_rows += rows
            total_processed += processed


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except KeyError as ex:
        print("csv_collation_summary: %s" % repr(ex), file=sys.stderr)
        exit(1)

    finally:
        if cmd and cmd.verbose:
            print("csv_collation_summary: total files: %d rows: %d processed: %d" %
                  (file_count, total_rows, total_processed), file=sys.stderr)
