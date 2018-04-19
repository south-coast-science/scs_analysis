#!/usr/bin/env python3

"""
Created on 16 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_logger utility is used to convert from JSON format to comma-separated value (CSV) format.

The path into the JSON document is used to name the column in the header row, with JSON nodes separated by a period
('.') character.

All the leaf nodes of the first JSON document are included in the CSV. If subsequent JSON documents in the input stream
contain fields that were not in this first document, these extra fields are ignored.

SYNOPSIS
csv_logger.py [-e] [-v] TOPIC

EXAMPLES
./socket_receiver.py | ./csv_logger.py -e climate

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:50:27.641+00:00", "val": {"hmd": 59.6, "tmp": 23.8}}

DOCUMENT EXAMPLE - OUTPUT
tag,rec,val.hmd,val.tmp
scs-ap1-6,2018-04-04T14:50:38.394+00:00,59.7,23.8

SEE ALSO
scs_analysis/csv_reader
scs_analysis/csv_writer
"""

import sys

from scs_analysis.cmd.cmd_csv_logger import CmdCSVLogger

from scs_core.csv.csv_log import CSVLog
from scs_core.csv.csv_logger import CSVLogger
from scs_core.csv.csv_logger_conf import CSVLoggerConf

from scs_host.sys.host import Host


# TODO: fix "tag"

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    logger = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCSVLogger()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        if cmd.verbose:
            print(cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # CSVLoggerConf...
        conf = CSVLoggerConf.load(Host)

        if conf and cmd.verbose:
            print(conf, file=sys.stderr)

        # CSVLog...
        log = None if conf is None else CSVLog(conf.root_path, 'tag', cmd.topic)

        if log and cmd.verbose:
            print(log, file=sys.stderr)

        # CSVLogger...
        logger = None if log is None else CSVLogger(Host, log)

        if logger and cmd.verbose:
            print(logger, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = line.strip()

            if datum is None:
                break

            if logger:
                try:
                    logger.write(datum)

                except OSError as ex:
                    print("csv_logger: %s" % ex, file=sys.stderr)
                    sys.stderr.flush()

            # echo...
            if cmd.echo:
                print(datum)
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("csv_logger: KeyboardInterrupt", file=sys.stderr)

    finally:
        if logger is not None:
            logger.close()
