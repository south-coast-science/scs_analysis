#!/usr/bin/env python3

"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_monitor utility is used to retrieve configuration information relating to one or more devices.
Flags enable the selection of either the latest recorded configuration for the device(s), or a history of
configuration changes. In the case of historical reports, either all the field values can be returned, or
only those that changed from the previous recording.

SYNOPSIS
configuration_monitor.py [-c CREDENTIALS] [-t TAG [-x]] { -l | -f | -d | -o } [-i INDENT] [-v]

EXAMPLES
configuration_monitor.py -t scs-bgx-401 -d | node.py -s | csv_writer.py -s

SEE ALSO
scs_analysis/configuration_csv
scs_analysis/configuration_monitor_check
scs_analysis/monitor_auth

scs_mfr/configuration
"""

import sys

from scs_analysis.cmd.cmd_configuration_monitor import CmdConfigurationMonitor
from scs_analysis.handler.batch_download_reporter import BatchDownloadReporter

from scs_core.aws.manager.configuration.configuration_finder import ConfigurationFinder
from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException

from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdConfigurationMonitor()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('configuration_monitor', verbose=cmd.verbose)
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

        # ConfigurationFinder...
        reporter = BatchDownloadReporter()
        finder = ConfigurationFinder(reporter=reporter)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        response = finder.find(auth.id_token, cmd.tag_filter, cmd.exact_match, cmd.response_mode())
        items = list(response)

        print(JSONify.dumps(sorted(items), indent=cmd.indent))
        logger.info('retrieved: %s' % len(items))


        # ------------------------------------------------------------------------------------------------------------
        # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
