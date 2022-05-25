#!/usr/bin/env python3

"""
Created on 24 May 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

# --------------------------------------------------------------------------------------------------------------------

v_cal = -250


def zero(output_mv_ppm, we_v):
    output_v_ppb = output_mv_ppm / 1000000.0
    zero_v = -((v_cal * output_v_ppb) - we_v)

    return round(zero_v * 1000.0, 2)


# --------------------------------------------------------------------------------------------------------------------

# 173...
zero_mv = zero(51.68, 0.06246)
print("173 - zero_mv: %s" % zero_mv)

# 174...
zero_mv = zero(28.05, 0.03958)
print("174 - zero_mv: %s" % zero_mv)

# 175...
zero_mv = zero(34.12, 0.03701)
print("175 - zero_mv: %s" % zero_mv)

# 176...
zero_mv = zero(36.51, 0.03767)
print("176 - zero_mv: %s" % zero_mv)

# 177...
zero_mv = zero(29.37, 0.03671)
print("177 - zero_mv: %s" % zero_mv)

# 178...
zero_mv = zero(37.97, 0.03656)
print("178 - zero_mv: %s" % zero_mv)
