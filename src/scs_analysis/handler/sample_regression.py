"""
Created on 16 Mar 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

class SampleRegression(object):
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

        self.__func = LinearRegression(tally, time_relative=True)


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

        if not self.__func.has_regression():
            return None

        slope, intercept = self.__func.line()

        if slope is None:
            return None

        target = PathDict()

        for path in sample.paths():
            if path == self.__path:
                target.append(self.__path + '.src', value)
                target.append(self.__path + '.slope', round(slope, self.__precision))
                target.append(self.__path + '.intercept', round(intercept, self.__precision))
            else:
                target.copy(sample, path)

        return target.node()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "SampleRegression:{path:%s, func:%s}" % (self.__path, self.__func)
