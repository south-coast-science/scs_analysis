"""
Created on 10 Mar 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

from collections import OrderedDict

from scs_core.csv.csv_writer import CSVWriter

from scs_core.data.json import JSONable
from scs_core.data.str import Str
from scs_core.data.timedelta import Timedelta


# --------------------------------------------------------------------------------------------------------------------

class CSVSegmentor(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, max_interval: Timedelta, file_prefix):
        """
        Constructor
        """
        self.__max_interval = max_interval                      # timedelta
        self.__file_prefix = file_prefix                        # string
        self.__blocks = []                                      # array of CSVContiguousBlock


    def __len__(self):
        return len(self.__blocks)


    # ----------------------------------------------------------------------------------------------------------------

    def collate(self, rec, jstr):
        # initialise...
        if not self.__blocks:
            self.__blocks.append(CSVContiguousBlock.construct(None, rec, self.file_prefix))

        current_block = self.__blocks[-1]

        interval = None if current_block.end is None else rec - current_block.end

        # end of block...
        if interval is not None and interval > self.max_interval:
            current_block.close()

            # new block...
            current_block = CSVContiguousBlock.construct(interval, rec, self.file_prefix)
            self.__blocks.append(current_block)

        # append...
        current_block.append(interval, rec, jstr)


    def close(self):
        for block in self.__blocks:
            block.close()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def max_interval(self):
        return self.__max_interval


    @property
    def file_prefix(self):
        return self.__file_prefix


    @property
    def blocks(self):
        return self.__blocks


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CSVSegmentor:{max_interval:%s, file_prefix:%s, blocks:%s}" % \
               (self.max_interval, self.file_prefix, Str.collection(self.blocks))


# --------------------------------------------------------------------------------------------------------------------

class CSVContiguousBlock(JSONable):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------
    # e.g. scs-bgx-431-ref-particulates-N2-climate-2019_15min_clipped_2020-03-10T16-00-18Z.csv

    @classmethod
    def construct(cls, prev_interval, start, file_prefix):
        if file_prefix is None:
            return cls(prev_interval, start, None)

        file_name = '-'.join((file_prefix,  start.as_iso8601().replace(':', '-'))) + '.csv'
        return cls(prev_interval, start, CSVWriter(file_name))


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, prev_interval, start, writer):
        """
        Constructor
        """
        self.__start = start                            # LocalizedDatetime
        self.__writer = writer                          # CSVWriter or None

        self.__prev_interval = prev_interval            # timedelta
        self.__max_interval = None                      # timedelta

        self.__end = None                               # LocalizedDatetime
        self.__count = 0                                # int


    # ----------------------------------------------------------------------------------------------------------------

    def append(self, interval, rec, jstr):
        if self.__writer:
            self.__writer.write(jstr)

        if self.count > 0 and (self.__max_interval is None or interval > self.__max_interval):
            self.__max_interval = interval

        self.__end = rec
        self.__count += 1


    def close(self):
        if self.__writer:
            self.__writer.close()


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self):
        jdict = OrderedDict()

        jdict['start'] = self.start.as_json()
        jdict['end'] = self.end.as_json()

        jdict['prev-interval'] = None if self.prev_interval is None else \
            Timedelta.construct(self.prev_interval).as_json()

        jdict['max-interval'] = None if self.max_interval is None else \
            Timedelta.construct(self.max_interval).as_json()

        jdict['count'] = self.count

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def start(self):
        return self.__start


    @property
    def end(self):
        return self.__end


    @property
    def prev_interval(self):
        return self.__prev_interval


    @property
    def max_interval(self):
        return self.__max_interval


    @property
    def count(self):
        return self.__count


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CSVContiguousBlock:{start:%s, end:%s, prev_interval:%s, max_interval:%s, count:%s, writer:%s}" % \
               (self.start, self.end, self.prev_interval, self.max_interval, self.count, self.__writer)
