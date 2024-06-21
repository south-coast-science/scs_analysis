#!/usr/bin/env python3

"""
Created on 9 Apr 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_topic_origin utility is used to discover the datetime of the earliest recorded publication on the given
topic(s), for a device, or for all topics known to aws_byline.

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
aws_topic_origin.py [-c CREDENTIALS] [-i INDENT] [-v] { -a | -d DEVICE | -t TOPIC_1 [...TOPIC_N] }

EXAMPLES
aws_topic_origin.py -vi4 -c super -d scs-be2-806
aws_topic_origin.py -v -c super -a | node.py -s | csv_writer.py -v origins-2024-04-10.csv

DOCUMENT EXAMPLE
{"topic": "ricardo/gatwick/loc/1/gases", "device": "scs-bgx-507", "rec": "2019-05-10T09:17:39Z",
"expiry": "2019-05-17T09:17:46Z"}

SEE ALSO
scs_analysis/aws_byline
scs_analysis/aws_topic_history
scs_analysis/cognito_user_credentials

scs_lambda/aws_message_delete
"""

import sys

from scs_analysis.cmd.cmd_aws_topic_origin import CmdAWSTopicOrigin
from scs_analysis.handler.batch_download_reporter import BatchDownloadReporter

from scs_core.aws.manager.byline.byline_finder import BylineFinder
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

        byline_finder = BylineFinder(reporter=BatchDownloadReporter('bylines'))
        origin_finder = TopicOriginFinder(reporter=BatchDownloadReporter('origins'))


        # ------------------------------------------------------------------------------------------------------------
        # check...

        if not Network.is_available():
            logger.info("waiting for network")
            Network.wait()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # topics...
        if cmd.all:
            topics = byline_finder.find_topics(auth.id_token)
        elif cmd.device:
            topics = byline_finder.find_topics_for_device(auth.id_token, cmd.device)
        else:
            topics = cmd.requested_topics

        # origins...
        origins = origin_finder.find_for_topics(auth.id_token, topics)

        print(JSONify.dumps(origins, indent=cmd.indent))
        logger.info("found: %s" % len(origins))


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
