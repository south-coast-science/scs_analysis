"""
Created on 17 Jan 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import logging
import time

from scs_core.data.timedelta import Timedelta
from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class BatchDownloadReporter(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, name):
        """
        Constructor
        """
        self.__name = name

        self.__block_count = 0
        self.__document_count = 0
        self.__start_time = time.time()

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        self.__block_count = 0
        self.__document_count = 0
        self.__start_time = time.time()


    def print(self, block_length, block_start=None):
        if Logging.level() > logging.INFO:
            return

        self.__block_count += 1
        self.__document_count += block_length
        elapsed_time = int(round(time.time() - self.__start_time))
        elapsed_delta = Timedelta(seconds=elapsed_time)
        elapsed = elapsed_delta.as_json()

        if block_start is None:
            self.__logger.info("%s: docs:%d elapsed:%s" %
                               (self.name, self.__document_count, elapsed))
        else:
            self.__logger.info("%s: block start:%s docs:%d elapsed:%s" %
                               (self.name, block_start, self.__document_count, elapsed))


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def name(self):
        return self.__name


    @property
    def block_count(self):
        return self.__block_count


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "BatchDownloadReporter:{name:%d, block_count:%d, document_count:%d, start_time:%d}" % \
               (self.name, self.block_count, self.__document_count, self.__start_time)
