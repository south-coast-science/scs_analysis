#!/usr/bin/env python3

"""
Created on 17 Oct 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The access_key utility is used to manage an AWS access key. The key is made up of a key ID (AWS_ACCESS_KEY_ID)
and a secret key (AWS_SECRET_ACCESS_KEY). The JSON key document managed by this utility is encrypted.

A password must be specified when the key is created and is required when the key is accessed.

SYNOPSIS
access_key.py [{ -s | -d }] [-v]

EXAMPLES
./access_key.py -s

FILES
~/SCS/aws/access_key.json

DOCUMENT EXAMPLE
{"key-id": "123", "secret-key": "456"}

SEE ALSO
scs_analysis/aws_bucket

RESOURCES
https://stackoverflow.com/questions/42568262/how-to-encrypt-text-with-a-password-in-python
"""

import sys

from scs_analysis.cmd.cmd_access_key import CmdAccessKey

from scs_core.aws.client.access_key import AccessKey
from scs_core.data.json import JSONify
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    access_key = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdAccessKey()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('access_key', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.set:
            access_key = AccessKey.from_user()
            password = AccessKey.password_from_user()

            access_key.save(Host, encryption_key=password)

        elif cmd.delete:
            AccessKey.delete(Host)

        else:
            password = AccessKey.password_from_user()

            try:
                access_key = AccessKey.load(Host, encryption_key=password)
            except (KeyError, ValueError):
                logger.error("incorrect password")
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # end...

        if access_key:
            print(JSONify.dumps(access_key))

    except KeyboardInterrupt:
        print(file=sys.stderr)
