#!/usr/bin/env python3

"""
Created on 23 May 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import logging

from scs_analysis.handler.batch_download_reporter import BatchDownloadReporter

from scs_core.aws.manager.lambda_message_manager import MessageManager

from scs_core.data.datetime import LocalizedDatetime
# from scs_core.data.json import JSONify

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------
Logging.config('test', level=logging.INFO)
logger = Logging.getLogger()

topic = "south-coast-science-dev/cube/device/praxis-opcube-000001/status"
# topic = "south-coast-science-dev/mobile/device/praxis-handheld-000008/status"

start = LocalizedDatetime.construct_from_iso8601("2023-09-01T00:00:00Z")
end = LocalizedDatetime.construct_from_iso8601("2023-10-01T00:01:00Z")

checkpoint =  '**:00:00'

# reporter...
Logging.config('lambda_message_manager_test')

# message manager...
message_manager = MessageManager(reporter=BatchDownloadReporter('messages'), api_key='NE33-2RL-1')
print(message_manager)

#     def find_for_topic(self, topic, start, end, path, fetch_last, checkpoint, include_wrapper, rec_only,
#                        min_max, exclude_remainder, fetch_last_written_before, backoff_limit): '**:/15:00'

document = list(message_manager.find_for_topic(topic, start, end, None, False, checkpoint,
                                               False, False, False, False, False, None))
# print(JSONify.dumps(document))
print("-")

print(LocalizedDatetime.now().as_iso8601())

