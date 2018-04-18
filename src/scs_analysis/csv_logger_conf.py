#!/usr/bin/env python3

"""
Created on 18 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_logger_conf utility is used to specify the identity of a sensing device, as it appears on either the South Coast
Science / AWS or OpenSensors.io Community Edition messaging infrastructures.

The identity is also used to tag all environmental sensing records. It is therefore important that a device retains
a fixed identity throughout its lifetime.

SYNOPSIS
csv_logger_conf.py [-r ROOT_PATH] [-o DELETE_OLDEST] [-v]

EXAMPLES
./csv_logger_conf.py -r /Users/bruno/SCS/logs -o

DOCUMENT EXAMPLE
{"root-path": "/Volumes/SCS/data", "delete-oldest": true}

FILES
~/SCS/conf/csv_logger_conf.json

SEE ALSO
scs_dev/csv_logger
"""

import sys

from scs_core.data.json import JSONify
from scs_core.csv.csv_logger_conf import CSVLoggerConf
from scs_core.sys.filesystem import Filesystem

from scs_host.sys.host import Host

from scs_analysis.cmd.cmd_logger_conf import CmdLoggerConf


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdLoggerConf()

    if cmd.verbose:
        print(cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # check for existing document...
    conf = CSVLoggerConf.load(Host)


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    if cmd.set():
        if conf is None and not cmd.is_complete():
            print("csv_logger_conf: No configuration is present. You must therefore set all fields:", file=sys.stderr)
            cmd.print_help(sys.stderr)
            exit(1)

        root_path = conf.root_path if cmd.root_path is None else cmd.root_path
        delete_oldest = conf.delete_oldest if cmd.delete_oldest is None else cmd.delete_oldest

        try:
            Filesystem.mkdir(root_path)
        except PermissionError:
            print("csv_logger_conf: You do not have permission to create that directory.", file=sys.stderr)
            exit(1)


        conf = CSVLoggerConf(root_path, delete_oldest)
        conf.save(Host)

    if conf:
        print(JSONify.dumps(conf))
