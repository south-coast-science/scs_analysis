#!/usr/bin/env python3

from scs_analysis.handler.csv_collator import CSVCollatorBin


# --------------------------------------------------------------------------------------------------------------------

filename = 'scs-bgx-431-ref-particulates-N2-climate-2019_15min_clipped_085p0_090p0.csv'
print(filename)
print("-")

try:
    low, high = CSVCollatorBin.parse(filename)
    print("low:%s high:%s" % (low, high))

except ValueError as ex:
    print("error: %s" % ex)
