"""
Created on 20 Feb 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.csv.csv_writer import CSVWriter


# --------------------------------------------------------------------------------------------------------------------

class CSVCollatorBin(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, lower, upper, file_prefix):
        file_name = file_prefix + cls.__infix(lower) + cls.__infix(upper) + '.csv'
        writer = CSVWriter(file_name)

        return CSVCollatorBin(lower, upper, writer)


    @classmethod
    def __infix(cls, bound):
        return str.replace("_%04.1f" % bound, ".", "p")


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, lower, upper, writer):
        """
        Constructor
        """
        self.__lower = lower
        self.__upper = upper
        self.__writer = writer

        self.__count = 0


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
