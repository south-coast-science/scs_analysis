#!/usr/bin/env python3

"""
Created on 12 Sep 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_report utility is used to generate a configuration CSV file by remotely interrogating the specified
device. The result is written to a CSV file named conf-scs-TYPE-NUMBER.csv

The utility is normally run in the directory that is scanned for raw report CSVs, such as
/Users/bruno/gbb/Production/ConfigurationGenerator/RawConfigs

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
configuration_report.py [-c CREDENTIALS] [-v] DEVICE_TAG_1 [...DEVICE_TAG_N]

EXAMPLES
configuration_report.py -v -c super scs-opc-245

SEE ALSO
scs_analysis/cognito_user_credentials
scs_analysis/device_controller

scs_mfr/configuration
"""

import sys

from scs_analysis.cmd.cmd_configuration_report import CmdConfigurationReport

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_device_finder import CognitoDeviceFinder
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPNotFoundException

from scs_core.estate.device_tag import DeviceTag

from scs_core.sys.command import Command
from scs_core.sys.filesystem import Filesystem
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdConfigurationReport()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('configuration_report', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        credentials = CognitoClientCredentials.load_for_user(Host, name=cmd.credentials_name)

        if not credentials:
            exit(1)

        gatekeeper = CognitoLoginManager()
        auth = gatekeeper.user_login(credentials)

        if not auth.is_ok():
            logger.error("login: %s." % auth.authentication_status.description)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        finder = CognitoDeviceFinder()
        clu = Command(verbose=cmd.verbose)


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        for device_tag in cmd.device_tags:
            if not DeviceTag.is_valid(device_tag):
                logger.error("the device tag '%s' is not valid." % device_tag)
                exit(2)

            try:
                finder.get_by_tag(auth.id_token, device_tag)
            except HTTPNotFoundException:
                logger.error("no device found for tag: '%s'." % device_tag)
                exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        credentials = ['-c', cmd.credentials_name] if cmd.credentials_name else []

        for device_tag in cmd.device_tags:
            output_file = 'conf-%s.csv' % device_tag
            cmd_args = ['device_controller.py'] + credentials + ['-t', device_tag, '-m', '"configuration -t"', '-s',
                                                                 '>', output_file]
            p = clu.s(cmd_args, abort_on_fail=False)

            if p.returncode != 0:
                Filesystem.rm(output_file)


        # ------------------------------------------------------------------------------------------------------------
        # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)
