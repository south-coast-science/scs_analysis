"""
Created on 2 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import re

from collections import OrderedDict

from scs_core.csv.csv_writer import CSVWriter

from scs_core.data.datum import Datum
from scs_core.data.json import JSONable


# --------------------------------------------------------------------------------------------------------------------

class CSVCollator(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, dataset_lower, dataset_upper, delta, file_prefix):
        bins = []

        bin_lower = dataset_lower
        numeric_format = Datum.format(dataset_upper, True)

        while bin_lower < dataset_upper:
            bin_upper = bin_lower + delta
            bins.append(CSVCollatorBin.construct(bin_lower, bin_upper, file_prefix, numeric_format))

            bin_lower = bin_upper

        return CSVCollator(dataset_lower, delta, bins)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, dataset_lower, delta, bins):
        """
        Constructor
        """
        self.__dataset_lower = dataset_lower            # float
        self.__delta = delta                            # float
        self.__bins = bins                              # array of CSVCollatorBin

        self.__max_bin_index = len(bins) - 1            # int


    # ----------------------------------------------------------------------------------------------------------------

    def collate(self, value, jstr):
        index = int((value - self.__dataset_lower) // self.__delta)

        if index < 0 or index > self.__max_bin_index:
            return False

        self.__bins[index].append(jstr)

        return True


    def close(self):
        for b in self.__bins:
            b.close()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def dataset_lower(self):
        return self.__dataset_lower


    @property
    def delta(self):
        return self.__delta


    @property
    def bins(self):
        return self.__bins


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CSVCollator:{dataset_lower:%s, delta:%s, bins:%s}" % \
               (self.dataset_lower, self.delta, self.bins)


# --------------------------------------------------------------------------------------------------------------------

class CSVCollatorBin(JSONable):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------
    # e.g. scs-bgx-431-ref-particulates-N2-climate-2019_15min_clipped_085p0_090p0.csv

    @classmethod
    def construct(cls, lower, upper, file_prefix, numeric_format):
        if file_prefix is None:
            return cls(lower, upper, None)

        file_name = file_prefix + cls.__infix(numeric_format, lower) + cls.__infix(numeric_format, upper) + '.csv'
        writer = CSVWriter(file_name)

        return cls(lower, upper, writer)


    @classmethod
    def __infix(cls, numeric_format, bound):
        return str.replace("_" + numeric_format % bound, ".", "p")


    @staticmethod
    def parse(filename):
        match = re.match(r'.*_(\d+)p(\d+)_(\d+)p(\d+)\.csv$', filename)

        if match is None:
            raise ValueError(filename)

        fields = match.groups()

        low = float('.'.join(fields[0:2]))
        high = float('.'.join(fields[2:4]))

        return low, high


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, lower, upper, writer):
        """
        Constructor
        """
        self.__lower = lower                            # float
        self.__upper = upper                            # float
        self.__writer = writer                          # CSVWriter

        self.__count = 0                                # int


    # ----------------------------------------------------------------------------------------------------------------

    def append(self, datum):
        if self.__writer:
            self.__writer.write(datum)

        self.__count += 1


    def close(self):
        if self.__writer:
            self.__writer.close()


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self, **kwargs):
        jdict = OrderedDict()

        jdict['lower'] = self.lower
        jdict['upper'] = self.upper
        jdict['count'] = self.count

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def lower(self):
        return self.__lower


    @property
    def upper(self):
        return self.__upper


    @property
    def count(self):
        return self.__count


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CSVCollatorBin:{lower:%s, upper:%s, count:%s, writer:%s}" % \
               (self.lower, self.upper, self.count, self.__writer)
