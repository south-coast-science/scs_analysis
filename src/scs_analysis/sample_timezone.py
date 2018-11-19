#!/usr/bin/env python3

"""
Created on 14 Nov 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The sample_timezone utility is used to shift the rec datetime field from the given UTC offset to the specified offset.

Not easy...

SYNOPSIS
sample_timezone.py { -n TIMEZONE_NAME | -o TIMEZONE_OFFSET }

EXAMPLES
sample_timezone.py -n Europe/Athens
sample_timezone.py -o +02:00

DOCUMENT EXAMPLE - OUTPUT
2018-04-05T18:42:03.702+00:00

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
"""

