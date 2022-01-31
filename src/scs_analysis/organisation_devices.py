#!/usr/bin/env python3

"""
Created on 19 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The organisation_devices utility is used to

SYNOPSIS
organisation_devices.py [-c CREDENTIALS] { -F { -l ORG_LABEL | -t DEVICE_TAG } | \
-C -l ORG_LABEL -t DEVICE_TAG -p PATH_ROOT GROUP LOCATION -d DEPLOYMENT_LABEL | \
-E -l ORG_LABEL -t DEVICE_TAG -p PATH_ROOT GROUP LOCATION | \
-D -t DEVICE_TAG } \
[-i INDENT] [-v]

EXAMPLES
organisation_devices.py -F -l NARA

DOCUMENT EXAMPLE
{"DeviceTag": "scs-bgx-401", "OrgID": 1, "DevicePath": "south-coast-science-demo/brighton/loc/1/",
"EnvironmentPath": "south-coast-science-demo/brighton/device/praxis-000401/",
"StartDatetime": "2022-01-17T10:40:04Z", "EndDatetime": null,
"DeploymentLabel": "Preston Circus"}

SEE ALSO
scs_analysis/cognito_credentials
"""

import requests
import sys

from scs_analysis.cmd.cmd_organisation_devices import CmdOrganisationDevices

from scs_core.aws.config.project import Project

from scs_core.aws.security.cognito_login_manager import CognitoLoginManager
from scs_core.aws.security.cognito_user import CognitoUserCredentials

from scs_core.aws.security.organisation import Organisation, OrganisationPathRoot, OrganisationDevice
from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.sys.http_exception import HTTPException
from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    credentials = None
    auth = None
    cognito = None
    org = None
    report = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdOrganisationDevices()

        if not cmd.is_valid():
            cmd.print_help(sys.stderr)
            exit(2)

        Logging.config('organisation_devices', verbose=cmd.verbose)
        logger = Logging.getLogger()

        logger.info(cmd)

        if cmd.org_label is not None and not Organisation.is_valid_label(cmd.org_label):
            logger.error("the organisation label '%s' is not valid." % cmd.org_label)
            exit(2)

        if cmd.device_tag is not None and not OrganisationDevice.is_valid_tag(cmd.device_tag):
            logger.error("the device tag '%s' is not valid." % cmd.device_tag)
            exit(2)

        if cmd.project_organisation is not None and \
                not OrganisationPathRoot.is_valid_path_root(cmd.project_organisation):
            logger.error("the path root '%s' is not valid." % cmd.project_organisation)
            exit(2)

        if cmd.project_location is not None and not Datum.is_int(cmd.project_location):
            logger.error("the project location '%s' must be an integer." % cmd.project_location)
            exit(2)

        if cmd.deployment_label is not None and not OrganisationDevice.is_valid_deployment_label(cmd.deployment_label):
            logger.error("the deployment label '%s' is not valid." % cmd.deployment_label)
            exit(2)


        # ------------------------------------------------------------------------------------------------------------
        # auth...

        gatekeeper = CognitoLoginManager(requests)

        # CognitoUserCredentials...
        if not CognitoUserCredentials.exists(Host, name=cmd.credentials_name):
            logger.error("Cognito credentials not available.")
            exit(1)

        try:
            password = CognitoUserCredentials.password_from_user()
            credentials = CognitoUserCredentials.load(Host, name=cmd.credentials_name, encryption_key=password)
        except (KeyError, ValueError):
            logger.error("incorrect password")
            exit(1)

        try:
            auth = gatekeeper.login(credentials)

        except HTTPException as ex:
            logger.error(ex.data)
            exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        manager = OrganisationManager(requests)


        # ------------------------------------------------------------------------------------------------------------
        # validate...

        if cmd.org_label is not None:
            org = manager.get_organisation_by_label(auth.id_token, cmd.org_label)

            if org is None:
                logger.error("no organisation found for label: '%s'." % cmd.org_label)
                exit(1)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.find:
            if cmd.org_label is not None:
                report = manager.find_devices_by_organisation(auth.id_token, org.org_id)
            else:
                report = manager.find_devices_by_tag(auth.id_token, cmd.device_tag)

        if cmd.create:
            project = Project.construct(cmd.project_organisation, cmd.project_group, cmd.project_location)
            device_path = project.device_path + '/'
            location_path = project.location_path + '/'

            now = LocalizedDatetime.now()

            report = OrganisationDevice(cmd.device_tag, org.org_id, device_path, location_path, now, None,
                                        cmd.deployment_label)

            manager.assert_device(auth.id_token, report)

        if cmd.expire:
            project = Project.construct(cmd.project_organisation, cmd.project_group, cmd.project_location)
            device_path = project.device_path + '/'
            location_path = project.location_path + '/'

            report = manager.get_device(auth.id_token, cmd.device_tag, org.org_id,
                                        device_path, location_path)

            if report is None:
                logger.error("no device found.")
                exit(1)

            report.end_datetime = LocalizedDatetime.now()
            manager.assert_device(auth.id_token, report)

        if cmd.delete:
            project = Project.construct(cmd.project_organisation, cmd.project_group, cmd.project_location)
            device_path = project.device_path + '/'
            location_path = project.location_path + '/'

            manager.delete_device(auth.id_token, cmd.device_tag, org.org_id, device_path, location_path)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.data)
        exit(1)
