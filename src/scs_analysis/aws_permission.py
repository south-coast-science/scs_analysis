#!/usr/bin/env python3

"""
Created on 27 Feb 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The aws_permission utility is used to assert permissions for lambda aliases. The aliases must be of the form
LAMBDA:Production. The permission-changing script is obtained by editing the API gateway integration request and
copying the "Add permission command".

SYNOPSIS
aws_permission.py [-v] LAMBDA

EXAMPLES
aws_permission.py -v CognitoDevices
aws lambda add-permission \
--function-name "arn:aws:lambda:us-west-2:696437392763:function:${stageVariables.functionVersion}" \
--source-arn "arn:aws:execute-api:us-west-2:696437392763:6c2sfqt656/*/GET/CognitoDevices/retrieve/*" \
--principal apigateway.amazonaws.com \
--statement-id 87d057af-aba3-4bf3-8077-73c66469de71 \
--action lambda:InvokeFunction
"""

import subprocess
import sys

from scs_analysis.cmd.cmd_aws_permission import CmdAWSPermission
from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdAWSPermission()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('aws_permission', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        function_version = ':'.join((cmd.lambda_function, 'Production'))


        # ------------------------------------------------------------------------------------------------------------
        # run...

        command = ''
        for line in sys.stdin:
            component = line.strip()
            command += component.removesuffix('\\')

            if not component.endswith('\\'):
                break

        command = command.replace('${stageVariables.functionVersion}', function_version)
        logger.info(command)

        subprocess.run(command, shell=True)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        print(file=sys.stderr)
