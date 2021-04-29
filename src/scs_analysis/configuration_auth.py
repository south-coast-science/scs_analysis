#!/usr/bin/env python3

"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_auth utility is used to

A password must be specified when the key is created and is required when the key is accessed.

SYNOPSIS
configuration_auth.py [{ -s | -d }] [-v]

EXAMPLES
./configuration_auth.py -s

FILES
~/SCS/aws/configuration_auth.json

DOCUMENT EXAMPLE
{"email": "bruno.beloff@southcoastscience.com", "password": "XXX"}

SEE ALSO
scs_analysis/configuration_monitor
scs_analysis/configuration_monitor_status

RESOURCES
https://stackoverflow.com/questions/42568262/how-to-encrypt-text-with-a-password-in-python
"""

import sys

from scs_analysis.cmd.cmd_configuration_auth import CmdConfigurationAuth

from scs_core.aws.client.configuration_auth import ConfigurationAuth
from scs_core.data.json import JSONify
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    auth = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdConfigurationAuth()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('configuration_auth', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.set:
            auth = ConfigurationAuth.from_user()

            if not auth.has_valid_email_address():
                logger.error("invalid email address: %s." % auth.email_address)
                exit(1)

            auth.save(Host, encryption_key=auth.password)

        elif cmd.delete:
            ConfigurationAuth.delete(Host)

        else:
            password = ConfigurationAuth.password_from_user()

            try:
                auth = ConfigurationAuth.load(Host, encryption_key=password)
            except (KeyError, ValueError):
                logger.error("incorrect password.")
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # end...

        if auth:
            print(JSONify.dumps(auth))

    except KeyboardInterrupt:
        print(file=sys.stderr)
