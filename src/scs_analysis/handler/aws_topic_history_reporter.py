"""
Created on 17 Jan 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import sys
import time

from scs_core.data.timedelta import Timedelta


# --------------------------------------------------------------------------------------------------------------------

class AWSTopicHistoryReporter(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, verbose):
        """
        Constructor
        """
        self.__verbose = verbose

        self.__document_count = 0
        self.__start_time = time.time()


    # ----------------------------------------------------------------------------------------------------------------

    def print(self, block_start, block_length):
        if not self.__verbose:
            return

        self.__document_count += block_length
        elapsed_time = int(round(time.time() - self.__start_time))
        elapsed_delta = Timedelta(seconds=elapsed_time)

        print("aws_topic_history: block start:%s docs:%d elapsed:%s" %
              (block_start, self.__document_count, elapsed_delta.as_json()), file=sys.stderr)

        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSTopicHistoryReporter:{verbose:%s, document_count:%d, start_time:%d}" % \
               (self.__verbose, self.__document_count, self.__start_time)
