#!/usr/bin/env python3

"""
Created on 24 Dec 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_upload_interval utility is used to determine the end-to-end health of the data infrastructure. Specifically, it
reports on the time difference between a sense document being created on a device, and the same document being
ingested by the data storage system. Time difference is represented as:

DAYS-HOURS:MINUTES:SECONDS

The aws_upload_interval utility relies on the data format provided by the aws_topic_history utility - when invoked with
its -w ("wrapper") flag, the aws_topic_history output includes an "upload" field, indicating the date / time at which
the document was processed. The sense time is provided in the "payload.rec" field. The aws_upload_interval
utility reports on the difference between the two date / times in seconds.

The utility accepts input from stdin. If an input document is empty or is not well-formed JSON, the document is
ignored. If the document is well-formed JSON, but does not contain the required "upload" and "payload.rec" fields or
the fields are not in ISO 8601 format, then an error is reported, and the aws_upload_interval utility terminates.

SYNOPSIS
aws_upload_interval.py

EXAMPLES
./aws_topic_history.py unep/ethiopia/loc/1/climate -m1440 -w | ./aws_upload_interval.py

DOCUMENT EXAMPLE - INPUT
{"device": "scs-bbe-501", "topic": "unep/ethiopia/loc/1/climate", "upload": "2018-12-24T13:07:03Z",
"payload": {"val": {"hmd": 36.5, "tmp": 25.5}, "rec": "2018-12-24T13:07:01Z", "tag": "scs-bgx-501"}}

DOCUMENT EXAMPLE - OUTPUT
{"upload": "2018-12-24T13:07:03Z", "rec": "2018-12-24T13:07:01Z", "offset": "00-00:00:01"}

SEE ALSO
scs_analysis/aws_topic_history

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys

from scs_core.data.json import JSONify

from scs_core.aws.data.upload_interval import UploadInterval


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    interval = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            jstr = line.strip()

            try:
                interval = UploadInterval.construct_from_jstr(jstr)

            except (KeyError, ValueError) as ex:
                print("aws_upload_interval: %s for: %s on: %s" % (ex.__class__.__name__, ex, jstr), file=sys.stderr)
                exit(1)

            if interval is None:
                continue

            # report...
            print(JSONify.dumps(interval))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        pass
