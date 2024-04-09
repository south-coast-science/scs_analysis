#!/usr/bin/env python3

"""
Created on 9 Apr 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_topic_origin utility is used to

SYNOPSIS
aws_topic_origin.py [-c CREDENTIALS] [-i INDENT] [-v] TOPIC

EXAMPLES
aws_topic_origin.py -vi4 -c super acsoft/uk-urban/loc/960/particulates

DOCUMENT EXAMPLE - OUTPUT
{"topic": "acsoft/uk-urban/loc/960/particulates", "device": "scs-bgx-960", "rec": "2024-03-27T15:51:54Z"}

SEE ALSO
scs_analysis/aws_topic_history
scs_analysis/aws_topic_origin.py

scs_lambda/aws_message_delete
"""

import sys

from scs_analysis.cmd.cmd_aws_topic_origin import CmdAWSTopicOrigin

from scs_core.aws.manager.topic_origin.topic_origin_finder import TopicOriginFinder

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.client.http_exception import HTTPException
from scs_core.client.network import Network

from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSTopicOrigin()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('aws_topic_origin', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
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

        finder = TopicOriginFinder()


        # ------------------------------------------------------------------------------------------------------------
        # check...

        if not Network.is_available():
            logger.info("waiting for network")
            Network.wait()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        origin = finder.find(auth.id_token, cmd.topic)

        print(JSONify.dumps(origin, indent=cmd.indent))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
