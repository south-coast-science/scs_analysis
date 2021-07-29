#!/usr/bin/env python3

"""
Created on 28 Jul 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The baseline utility is used to

SYNOPSIS
baseline.py { -l | -d [-c CAUSE] } [-i INDENT] [-v] ID

EXAMPLES
baseline.py -d -cL 123

DOCUMENT EXAMPLE

SEE ALSO
scs_analysis/baseline_baseline_conf
"""

import requests
import sys

from scs_analysis.cmd.cmd_baseline import CmdBaseline

from scs_analysis.handler.aws_topic_history_reporter import AWSTopicHistoryReporter

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.client.monitor_auth import MonitorAuth

from scs_core.aws.manager.byline_manager import BylineManager
from scs_core.aws.manager.configuration_finder import ConfigurationFinder, ConfigurationRequest
from scs_core.aws.manager.lambda_message_manager import MessageManager

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.estate.baseline_conf import BaselineConf

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    latest_rec = None
    topic = None

    logger = None
    auth = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdBaseline()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('baseline', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # ConfigurationFinder...
        if not MonitorAuth.exists(Host):
            logger.error('MonitorAuth key not available.')
            exit(1)

        try:
            # auth = MonitorAuth.load(Host, encryption_key=MonitorAuth.password_from_user())
            auth = MonitorAuth.load(Host, encryption_key='beloff')
        except (KeyError, ValueError):
            logger.error('incorrect password.')
            exit(1)

        finder = ConfigurationFinder(requests, auth)

        # BaselineConf...
        baseline_conf = BaselineConf.load(Host)

        if baseline_conf is None:
            logger.error("BaselineConf is not available")
            exit(1)

        logger.info(baseline_conf)

        # APIAuth...
        api_auth = APIAuth.load(Host)

        if api_auth is None:
            logger.error("APIAuth is not available")
            exit(1)

        # BylineManager...
        byline_manager = BylineManager(api_auth)

        # reporter...
        reporter = AWSTopicHistoryReporter(cmd.verbose)

        # message manager...
        message_manager = MessageManager(api_auth, reporter=reporter)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # configuration...
        # response = finder.find(cmd.device_tag, True, ConfigurationRequest.MODE.LATEST)
        # print(response)
        # print("-")

        # bylines...
        group = byline_manager.find_bylines_for_device(cmd.device_tag)

        if group is None:
            logger.error("no bylines found for %s." % cmd.device_tag)
            exit(1)

        for byline in group.bylines:
            if not byline.topic.endswith("/gases"):
                continue

            if latest_rec is None or byline.rec > latest_rec:
                latest_rec = byline.rec
                topic = byline.topic

        if topic is None:
            logger.error("no gases topic found for %s." % cmd.device_tag)
            exit(1)

        logger.info("topic: %s" % topic)
        print("-")

        # data...
        now = LocalizedDatetime.now()
        start = baseline_conf.start_datetime(now)
        end = baseline_conf.end_datetime(now)

        data = list(message_manager.find_for_topic(topic, start, end, None, False, baseline_conf.checkpoint(),
                                                   False, False, False, False))

        if not data:
            logger.error("no data found for %s." % topic)
            exit(1)

        # minimums...
        minimums = {path: None for path in PathDict(data[0]).paths() if path.endswith(".cnc")}

        for i in range(len(data)):
            dictionary = PathDict(data[i])

            for path in minimums:
                value = int(round(float(dictionary.node(path))))
                if minimums[path] is None or value < minimums[path]['value']:
                    minimums[path] = {'index': i, 'value': value, 'datum': data[i]}

        print(JSONify.dumps(minimums, indent=4))
        print("-")

        for path, minimum in minimums.items():
            if minimum['index'] == 0:
                logger.error("warning: the first value for %s was the minimum value." % path)

            elif minimum['index'] == len(data) - 1:
                logger.error("warning: the last value for %s was the minimum value." % path)

        # corrections...
        gas_offsets = baseline_conf.gas_offsets

        for path in minimums:
            pieces = path.split(".")
            gas = pieces[len(pieces) - 2]       # TODO: distinguish between 'val' and 'exg' fields
            if gas in baseline_conf.gas_offsets:
                print(gas)

        # reboot...


    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        now = LocalizedDatetime.now().utc().as_iso8601()
        logger.error("%s: HTTP response: %s (%s) %s" % (now, ex.status, ex.reason, ex.data))
        exit(1)
