#!/usr/bin/env python3

"""
Created on 16 Feb 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_fit utility

SYNOPSIS
sample_fit.py -i IND_PATH -d DEP_PATH_1 [-l LOWER_BOUND] [-u UPPER_BOUND] [-p IND_PRECISION DEP_PRECISION] [-v]

EXAMPLES


DOCUMENT EXAMPLE - OUTPUT


RESOURCES
http://pyhyd.blogspot.com/2017/06/exponential-curve-fit-in-numpy.html
https://plot.ly/python/v3/exponential-fits/
https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly
"""

import sys

import scipy.stats as stats

from scs_analysis.cmd.cmd_sample_fit import CmdSampleFit

from scs_core.data.curve_fit import CurveFit
from scs_core.data.datum import Datum
from scs_core.data.json import JSONify
from scs_core.data.linear_equation import LinE, LinEC, LinEP1C, LinEP2C, LinEP3C
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    data = []
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleFit()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("sample_fit: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # CurveFit...
        curve = CurveFit([])


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # collect data...
        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)
            paths = datum.paths()

            data.append(datum)

            if cmd.ind_path not in paths:
                print("sample_fit: independent path not in datum: %s" % cmd.ind_path, file=sys.stderr)
                exit(1)

            try:
                ind_value = float(datum.node(cmd.ind_path))
            except ValueError:
                continue                                            # independent value is NaN - skip this row

            if cmd.lower is not None and ind_value < cmd.lower:
                continue

            if cmd.upper is not None and ind_value >= cmd.upper:
                continue

            if cmd.dep_path not in paths:
                print("sample_fit: dependent path not in datum: %s" % cmd.dep_path, file=sys.stderr)
                exit(1)

            try:
                dep_value = float(datum.node(cmd.dep_path))
            except ValueError:
                continue                                            # dependent value is NaN - skip this row

            curve.append(ind_value, dep_value)

            processed_count += 1

        # fit...
        for cls in LinE, LinEC, LinEP1C, LinEP2C, LinEP3C:
            popt, _ = curve.fit(cls.func, bounds=cls.default_coefficient_bounds())

            equation = cls.construct(popt)
            synthesized = [round(equation.compute(x), 3) for x in curve.independents()]

            if cmd.verbose:
                print("sample_fit: equation: %s" % equation, file=sys.stderr)
                print("sample_fit: equation: %s" % equation.display(), file=sys.stderr)
                print("sample_fit: equation: %s" % JSONify.dumps(equation.as_json()), file=sys.stderr)
                print("-", file=sys.stderr)

                print("sample_fit: empirical: %s" % curve.dependents(), file=sys.stderr)
                print("sample_fit: synthetic: %s" % synthesized, file=sys.stderr)
                print("-", file=sys.stderr)

                slope, intercept, rvalue, pvalue, stderr = stats.linregress(curve.dependents(), synthesized)
                r2 = rvalue ** 2

                print("sample_fit: r2: %0.6f" % r2, file=sys.stderr)
                print("=", file=sys.stderr)

                sys.stderr.flush()

            # append synthesized...
            for i in range(len(data)):
                ind_value = Datum.float(data[i].node(cmd.ind_path))
                synthesized = round(equation.compute(ind_value), 3) if ind_value in curve.independents() else None

                data[i].append('.'.join((equation.name(), cmd.dep_path)), synthesized)

        # report...
        for datum in data:
            print(JSONify.dumps(datum.as_json()))


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyError as ex:
        print("sample_fit: KeyError: %s" % ex, file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("sample_fit: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.verbose:
            print("sample_fit: documents: %d processed: %d" % (len(data), processed_count), file=sys.stderr)
