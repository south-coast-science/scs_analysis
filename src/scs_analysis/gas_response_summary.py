#!/usr/bin/env python3

"""
Created on 21 Jun 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The gas_response_summary utility is used to collect aggregated data from multiple devices for the purposes of
comparison of zero offset and sensitivity, for AAN-803 electrochems, SCD30 CO2 sensor, PID VOC sensor, and and
ML model outputs.

AAN-803 sources are:
* CO
* Ox

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
gas_response_summary.py [-c CREDENTIALS] [-s START] [-e END] [-i INDENT] [-v] DEVICE_TAG_1 [... DEVICE_TAG_N]

EXAMPLES
gas_response_summary.py -v -c super scs-bgx-531 scs-bgx-906 scs-bgx-913 | \
csv_writer.py -v -s scs-group-gases-2024-06-21.csv

DOCUMENT EXAMPLE
{"tag": "scs-bgx-531", "rec": "2024-06-21T08:53:00Z", "val":
{"Ox": {"cnc": {"min": 41.4, "mid": 46.4, "max": 59.2, "upper-range": 12.8}}},
"exg": {"src": "uE.1",
"val": {"NO2": {"cnc": {"min": 6.7, "mid": 12.3, "max": 19.6, "upper-range": 7.3}},
"NO": {"cnc": {"min": 3.4, "mid": 5.6, "max": 8.3, "upper-range": 2.7}},
"SO2": {"cnc": {"min": 1.2, "mid": 3.4, "max": 6.5, "upper-range": 3.1}}}}}

SEE ALSO
scs_analysis/cognito_user_credentials
scs_analysis/sample_range
"""

import sys

from collections import OrderedDict

from scs_analysis.cmd.cmd_gas_response_summary import CmdGasResponseSummary

from scs_core.aws.manager.byline.byline_finder import BylineFinder
from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.timedelta import Timedelta
from scs_core.data.json import JSONify

from scs_core.sys.command import Command
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    NON_ML_GASES = ['val.CO.cnc', 'val.CO2.cnc', 'val.Ox.cnc', 'val.VOC.cnc']
    logger = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdGasResponseSummary()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('gas_response_summary', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # authentication...

        credentials = CognitoClientCredentials.load_for_user(Host, name=cmd.credentials_name)

        if not credentials:
            exit(1)

        gatekeeper = CognitoLoginManager()
        auth = gatekeeper.user_login(credentials)

        if not auth.is_ok():
            logger.error("login: %s." % auth.authentication_status.description)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        byline_finder = BylineFinder()

        clu = Command(verbose=cmd.verbose)


        # ------------------------------------------------------------------------------------------------------------
        # validation...

        # datetimes...
        if cmd.end is None:
            end = LocalizedDatetime.now()
        else:
            end = LocalizedDatetime.construct_from_iso8601(cmd.end)
            if end is None:
                logger.error("the end time '%s' is invalid." % cmd.end)
                exit(2)

        if cmd.start is None:
            start = end - Timedelta(days=1)
        else:
            start = LocalizedDatetime.construct_from_iso8601(cmd.start)
            if start is None:
                logger.error("the start time '%s' is invalid." % cmd.start)
                exit(2)

        if end <= start:
            logger.error("invalid start and end times.")
            exit(2)

        # devices...
        device_bylines = OrderedDict()
        for device_tag in cmd.device_tags:
            bylines = byline_finder.find_bylines_for_device(auth.id_token, device_tag, include_messages=False)
            latest_gases_byline = bylines.latest_byline(suffix='/gases')

            if not latest_gases_byline:
                logger.error("the device '%s' has no gases byline." % device_tag)
                exit(2)

            device_bylines[device_tag] = latest_gases_byline.topic


        # ------------------------------------------------------------------------------------------------------------
        # run...

        credentials = ['-c', cmd.credentials_name] if cmd.credentials_name else []

        for device_tag, topic in device_bylines.items():
            logger.info("%s..." % device_tag)

            p = clu.o(['aws_topic_history.py'] + credentials + ['-s', start.as_iso8601(), '-e', end.as_iso8601(),
                                                                '-p', '**:/1:00', topic])

            p = clu.io(p, ['sample_aggregate.py', '-m'])
            p = clu.io(p, ['node.py', 'tag.mid', 'rec'] + NON_ML_GASES + ['exg.src.mid', 'exg.val'], no_verbose=True)
            p = clu.io(p, ['node.py', '-m', 'tag.mid', 'tag'], no_verbose=True)
            p = clu.io(p, ['node.py', '-m', 'exg.src.mid', 'exg.src'], no_verbose=True)
            p = clu.io(p, ['sample_range.py', '-u', '.cnc.'])

            print(JSONify.dumps(p.json(), indent=cmd.indent))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
