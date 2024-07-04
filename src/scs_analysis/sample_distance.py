#!/usr/bin/env python3

"""
Created on 10 Feb 2021

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The sample_distance utility is used to find the distance (in kilometres, to the nearest metre) between a given position,
and the position in each of the input GPS JSON documents. A command flag specifies the path to the node within the
document that is to be examined.

The quality of the GPS fix may be taken into account: if a quality is specified, then any GPS fix with a quality
(rounded to the nearest integer) below that level is discarded.

A simple, spherical model of the earth is used.

SYNOPSIS
sample_distance.py -p LAT LNG [-i ISO] [-q QUALITY] [-v] GPS_PATH

EXAMPLES
csv_reader.py -v scs-ph1-10-status-H2-15min.csv | \
sample_distance.py -v -p 51.4889752 -0.4418752 -q 1 val.gps | \
csv_writer.py -v scs-ph1-10-distance-H2-15min.csv

DOCUMENT EXAMPLE - INPUT
{"rec": "2020-12-09T21:00:00Z", "val": {"gps": {"pos": [51.48877673, -0.44155907], "elv": 33.3, "qual": 1.0},
"tag": "scs-ph1-10"}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2020-12-09T21:00:00Z", "gps": {"pos": [51.48877673, -0.44155907], "elv": 33.3, "qual": 1}, "dist": 0.031}

RESOURCES
Getting distance between two points based on latitude/longitude
https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
"""

import sys

from scs_analysis.cmd.cmd_sample_distance import CmdSampleDistance

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.position.gps_datum import GPSDatum
from scs_core.position.position import Position

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampleDistance()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    Logging.config('sample_distance', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        origin = Position(cmd.lat, cmd.lng)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        min_datum = None

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if datum is None:
                continue

            document_count += 1

            if not datum.has_sub_path(cmd.iso):
                logger.error("ISO node '%s' not present: %s" % (cmd.iso, line.strip()))
                exit(1)

            if not datum.has_sub_path(cmd.path):
                logger.error("GPS node '%s' not present: %s" % (cmd.path, line.strip()))
                exit(1)

            gps_node = datum.node(cmd.path)

            try:
                gps = GPSDatum.construct_from_jdict(gps_node)
                distance = gps.distance(origin, minimum_acceptable_quality=cmd.quality)

            except TypeError:
                gps = None
                distance = None

            if distance is None:
                continue

            report = PathDict()
            report.append('rec', datum.node(cmd.iso))
            report.append('gps', gps)
            report.append('dist', distance)

            print(JSONify.dumps(report))

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    finally:
        logger.info("documents: %d processed: %d" % (document_count, processed_count))
