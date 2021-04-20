#!/usr/bin/env python3
"""
Created on 30 Mar 2021

@author: Jade Page (jade.page@southcoastscience.com)
"""

# --------------------------------------------------------------------------------------------------------------------
import sys

from scs_analysis.cmd.cmd_aws_config_search import CmdAWSConfigSearch
from scs_core.data.json import JSONify
from scs_core.estate.config_search import ConfigurationSearcher

if __name__ == '__main__':


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSConfigSearch()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("aws_config_search: %s" % cmd, file=sys.stderr)

    # ----------------------------------------------------------------------------------------------------------------
    # run...
    config_searcher = ConfigurationSearcher()
    data = config_searcher.get_data()

    # if cmd.hostname:
    #     data = config_searcher.get_by_name(cmd.hostname)

    if type(data) == int:
        if data == 1 or data == 2:
            data = "invalid auth"
        if data == 3:
            data = "server error"

    if cmd.indent:
        print(JSONify.dumps(data, indent=3))
    else:
        print(JSONify.dumps(data))
