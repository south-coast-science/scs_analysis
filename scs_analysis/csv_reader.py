#!/usr/bin/env python3

'''
Created on 4 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./csv_reader.py temp.csv
'''

import sys

from scs_analysis.cmd.cmd_csv_reader import CmdCSVReader

from scs_core.csv.csv_reader import CSVReader


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    csv = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCSVReader()

        if cmd.verbose:
            print(cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resource...

        csv = CSVReader(cmd.filename)

        if cmd.verbose:
            print(csv, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for datum in csv.rows:
            print(datum)
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("csv_reader: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print("csv_reader: " + type(ex).__name__, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        if csv is not None:
            csv.close()
