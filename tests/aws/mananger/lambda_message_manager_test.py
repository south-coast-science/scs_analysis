#!/usr/bin/env python3

"""
Created on 23 May 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_analysis.handler.aws_topic_history_reporter import AWSTopicHistoryReporter

from scs_core.aws.client.api_auth import APIAuth
from scs_core.aws.manager.lambda_message_manager import MessageManager

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

topic = "south-coast-science-dev/mobile/device/praxis-handheld-000008/status"
# up_to = LocalizedDatetime.construct_from_iso8601('2020-05-24T00:00:00Z')
up_to = LocalizedDatetime.now()

# APIAuth...
api_auth = APIAuth.load(Host)
print(api_auth)

# reporter...
reporter = AWSTopicHistoryReporter(False)

# message manager...
message_manager = MessageManager(api_auth, reporter)
print(message_manager)

document = message_manager.find_latest_for_topic(topic, up_to)
print(JSONify.dumps(document))

