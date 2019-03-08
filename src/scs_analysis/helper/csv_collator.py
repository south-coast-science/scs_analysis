"""
Created on 2 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

from scs_core.csv.csv_writer import CSVWriter
from scs_core.data.datum import Datum


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
        form = Datum.format(dataset_upper, True)

        while bin_lower < dataset_upper:
            bin_upper = bin_lower + delta
            bins.append(CSVCollatorBin.construct(bin_lower, bin_upper, file_prefix, form))

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

        self.__bins[index].write(jstr)

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

class CSVCollatorBin(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, lower, upper, file_prefix, form):
        file_name = file_prefix + cls.__infix(form, lower) + cls.__infix(form, upper) + '.csv'
        writer = CSVWriter(file_name)

        return CSVCollatorBin(lower, upper, writer)


    @classmethod
    def __infix(cls, form, bound):
        return str.replace("_" + form % bound, ".", "p")


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

    def write(self, datum):
        self.__writer.write(datum)

        self.__count += 1


    def close(self):
        self.__writer.close()


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
