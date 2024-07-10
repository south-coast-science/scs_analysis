#!/usr/bin/env python3

"""
Created on 19 Jan 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis

DESCRIPTION
The organisation_devices utility is used to manage the relationship between organisations and Cognito devices. The
utility can find, create and delete these relationships.

Over a period of time, a device may pass from ownership by one organisation to ownership by another. Each
ownership period is represented by a separate record. Where the start of an ownership is not known, the start
datetime is recorded as 1970-01-01T00:00:00Z.

The --credentials flag is only required where the user wishes to store multiple identities. Setting the credentials
is done interactively using the command line interface.

SYNOPSIS
organisation_devices.py [-c CREDENTIALS] { -F { -l ORG_LABEL | -t DEVICE_TAG } |
-C -l ORG_LABEL -t DEVICE_TAG -p PATH_ROOT GROUP LOCATION -d DEPLOYMENT_LABEL | -D -t DEVICE_TAG } [-i INDENT] [-v]

EXAMPLES
organisation_devices.py -F -l "South Coast Science (Demo)"

organisation_devices.py -c super -vi4 -F -t scs-bgx-570

DOCUMENT EXAMPLE
[
    {
        "DeviceTag": "scs-bgx-570",
        "OrgID": 68,
        "DeploymentLabel": "Praxis / Urban @ Preston Circus, Brighton",
        "DevicePath": "south-coast-science-demo/brighton-urban/device/praxis-000570/",
        "LocationPath": "south-coast-science-demo/brighton-urban/loc/1/",
        "StartDatetime": "2021-07-30T10:42:38Z",
        "EndDatetime": null
    }
]

SEE ALSO
scs_analysis/cognito_devices
scs_analysis/cognito_user_credentials
"""

import sys

from scs_analysis.cmd.cmd_organisation_devices import CmdOrganisationDevices

from scs_core.aws.config.project import Project

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.aws.security.organisation import Organisation, OrganisationPathRoot, OrganisationDevice
from scs_core.aws.security.organisation_manager import OrganisationManager

from scs_core.client.http_exception import HTTPException

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.datum import Datum
from scs_core.data.json import JSONify

from scs_core.estate.device_tag import DeviceTag

from scs_core.sys.logging import Logging

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    logger = None
    org = None
    report = []

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

        if cmd.device_tag is not None and not DeviceTag.is_valid(cmd.device_tag):
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

        manager = OrganisationManager()


        # ------------------------------------------------------------------------------------------------------------
        # validation...

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

        if cmd.delete:
            manager.delete_device(auth.id_token, cmd.device_tag)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

        if report is not None:
            print(JSONify.dumps(report, indent=cmd.indent))

        if cmd.find:
            logger.info("found: %s" % len(report))

    except KeyboardInterrupt:
        print(file=sys.stderr)

    except HTTPException as ex:
        logger.error(ex.error_report)
        exit(1)

    except Exception as ex:
        logger.error(ex.__class__.__name__)
        exit(1)
