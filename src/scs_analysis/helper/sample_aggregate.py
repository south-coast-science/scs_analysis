"""
Created on 1 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import sys

from decimal import InvalidOperation

from scs_core.data.json import JSONify
from scs_core.data.linear_regression import LinearRegression
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict
from scs_core.data.precision import Precision


# --------------------------------------------------------------------------------------------------------------------

class SampleAggregate(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, min_max, include_tag, iso_path, nodes):
        """
        Constructor
        """
        self.__min_max = min_max
        self.__include_tag = include_tag
        self.__iso_path = iso_path
        self.__nodes = nodes

        self.__precisions = {}
        self.__regressions = {}

        self.__initialised = False
        self.__tag = None

        self.__output_count = 0


    # ----------------------------------------------------------------------------------------------------------------

    def has_value(self):
        for regression in self.__regressions.values():
            if regression.has_midpoint():
                return True

        return False


    def append(self, datetime: LocalizedDatetime, sample: PathDict):
        # initialise...
        if not self.__initialised:
            for node in self.__nodes:
                try:
                    paths = sample.paths(node)

                except KeyError:
                    continue

                except IndexError as ex:
                    paths = None
                    print("sample_aggregate: %s: IndexError: %s" % (node, ex), file=sys.stderr)
                    sys.stderr.flush()
                    exit(1)

                for path in paths:
                    self.__precisions[path] = Precision()
                    self.__regressions[path] = LinearRegression()

            self.__initialised = True

        # tag...
        if self.__include_tag:
            if sample.has_path('tag'):
                self.__tag = sample.node('tag')

        # values...
        for path in self.__precisions.keys():
            try:
                value = sample.node(path)
            except KeyError:
                continue

            if value is None:
                continue

            try:
                self.__precisions[path].widen(value)
                self.__regressions[path].append(datetime, value)
            except InvalidOperation:
                continue


    def reset(self):
        for path in self.__regressions.keys():
            self.__regressions[path].reset()


    def report(self, localised_datetime):
        report = PathDict()

        # tag...
        if self.__tag:
            report.append('tag', self.__tag)

        # rec...
        report.append(self.__iso_path, localised_datetime.as_iso8601())

        # values...
        for path, precision in self.__precisions.items():
            regression = self.__regressions[path]

            if self.__regressions[path].has_midpoint():
                _, midpoint = regression.midpoint()

                if self.__min_max:
                    report.append(path + '.min', round(regression.min(), precision.digits))
                    report.append(path + '.mid', round(midpoint, precision.digits))
                    report.append(path + '.max', round(regression.max(), precision.digits))

                else:
                    report.append(path, round(midpoint, precision.digits))

        return report


    def print(self, localised_datetime):
        print(JSONify.dumps(self.report(localised_datetime)))
        sys.stdout.flush()

        self.__output_count += 1


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def output_count(self):
        return self.__output_count


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        regressions = '[' + ', '.join(topic + ':' + str(reg) for topic, reg in self.__regressions.items()) + ']'

        return "SampleAggregate:{min_max:%s, include_tag:%s iso_path:%s output_count:%s, regressions:%s}" % \
               (self.__min_max, self.__include_tag, self.__iso_path, self.output_count, regressions)
