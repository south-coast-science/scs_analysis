"""
Created on 17 Jan 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys
import time


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
        elapsed_time = round(time.time() - self.__start_time, 1)

        print("aws_topic_history: block start:%s docs:%d elapsed:%0.1f" %
              (block_start, self.__document_count, elapsed_time), file=sys.stderr)

        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSTopicHistoryReporter:{verbose:%s, document_count:%d, start_time:%d}" % \
               (self.__verbose, self.__document_count, self.__start_time)
