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

        self.__block_count = 0
        self.__document_count = 0
        self.__start_time = time.time()


    # ----------------------------------------------------------------------------------------------------------------

    def print(self, block_start, block_length):
        if not self.__verbose:
            return

        self.__block_count += 1
        self.__document_count += block_length
        elapsed_time = int(round(time.time() - self.__start_time))
        elapsed_delta = Timedelta(seconds=elapsed_time)

        print("aws_topic_history: block start:%s docs:%d elapsed:%s" %
              (block_start, self.__document_count, elapsed_delta.as_json()), file=sys.stderr)

        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def block_count(self):
        return self.__block_count


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSTopicHistoryReporter:{verbose:%s, block_count:%d, document_count:%d, start_time:%d}" % \
               (self.__verbose, self.block_count, self.__document_count, self.__start_time)
