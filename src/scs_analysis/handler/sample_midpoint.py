"""
Created on 17 Mar 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

class SampleMidpoint(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, path, tally, precision):
        """
        Constructor
        """
        self.__path = path
        self.__precision = precision

        self.__func = LinearRegression(tally, time_relative=False)


    # ----------------------------------------------------------------------------------------------------------------

    def datum(self, sample):
        if not sample.has_path(self.__path):
            return None

        try:
            rec_node = sample.node('rec')
        except KeyError:
            return None

        rec = LocalizedDatetime.construct_from_jdict(rec_node)
        value = sample.node(self.__path)

        self.__func.append(rec, value)

        if not self.__func.has_midpoint():
            return None

        mid_rec, mid = self.__func.midpoint()

        if rec is None:
            return None

        target = PathDict()

        target.append('rec', rec.as_iso8601())
        target.append('mid-rec', mid_rec.as_iso8601())

        target.append(self.__path + '.src', value)
        target.append(self.__path + '.mid', round(mid, self.__precision))

        return target.node()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "SampleMidpoint:{path:%s, precision:%s, func:%s}" % (self.__path, self.__precision, self.__func)
