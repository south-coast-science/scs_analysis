#!/usr/bin/env python3

"""
Created on 20 Apr 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The configuration_monitor_check utility is used to report on the configuration monitor's attempt to access all of
the devices known to the system. Status levels are:

* NOR - NO RESPONSE
* ERR - ERROR
* M - MALFORMED:
* MSA - MALFORMED:SAMPLE
* MCO - MALFORMED:CONFIG
* NSP - NOT SUPPORTED
* R - RECEIVED:
* RNW - RECEIVED:NEW
* RUN - RECEIVED:UNCHANGED
* RUP - RECEIVED:UPDATED

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
configuration_monitor_check.py [-c CREDENTIALS] [{ -f DEVICE_TAG | -t DEVICE_TAG [-x] [-o] | -r CODE }] [-i INDENT] [-v]

EXAMPLES
configuration_monitor_check.py -r ERR | node.py -s | csv_writer.py

DOCUMENT EXAMPLE
{"tag": "scs-ph1-26", "rec": "2021-05-18T14:36:00Z", "result": "ERROR",
"context": ["TimeoutExpired(['./configuration'], 30)"]}

SEE ALSO
scs_analysis/cognito_user_credentials
scs_analysis/configuration_csv
scs_analysis/configuration_monitor
scs_analysis/monitor_auth

scs_mfr/configuration

BUGS
Result code not currently in use.
"""

import sys

from scs_analysis.cmd.cmd_configuration_monitor_check import CmdConfigurationMonitorCheck

from scs_core.aws.manager.configuration.configuration_check_finder import ConfigurationCheckFinder
from scs_core.aws.manager.configuration.configuration_check_requester import ConfigurationCheckRequester

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

        cmd = CmdConfigurationMonitorCheck()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('configuration_monitor_check', verbose=cmd.verbose)
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

        finder = ConfigurationCheckFinder()
        requester = ConfigurationCheckRequester()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.force:
            response = requester.request(auth.id_token, cmd.force)
            print(response.result, file=sys.stderr)
            exit(0 if response.result == 'OK' else 1)

        response = finder.find(auth.id_token, cmd.tag_filter, cmd.exact_match, cmd.response_mode())

        print(JSONify.dumps(sorted(response.items), indent=cmd.indent))
        logger.info('retrieved: %s' % len(response.items))


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
