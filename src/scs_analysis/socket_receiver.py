#!/usr/bin/env python3

"""
Created on 18 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The XX utility is used to .

EXAMPLES
./socket_receiver.py -p 2002
"""

import sys

from scs_analysis.cmd.cmd_socket_receiver import CmdSocketReceiver

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

from scs_host.comms.network_socket import NetworkSocket


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSocketReceiver()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    receiver = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        receiver = NetworkSocket('', cmd.port)

        if cmd.verbose:
            print(receiver, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for message in receiver.read():
            print(message)
            sys.stdout.flush()

            receiver.ack()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("socket_receiver: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        if receiver:
            receiver.close()
