#!/usr/bin/env python3

"""
Created on 19 Dec 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires APIAuth document.

Creates ClientAuth document.

document example:
{"user_id": "south-coast-science-test-user", "client-id": "5403", "client-password": "rtxSrK2f"}

command line examples:
./osio_client_auth.py -u south-coast-science-test-user -v
"""

import sys

from scs_core.data.json import JSONify

from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.osio.config.project_client import ProjectClient
from scs_core.osio.manager.device_manager import DeviceManager
from scs_core.osio.manager.user_manager import UserManager

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host

from scs_analysis.cmd.cmd_osio_client_auth import CmdOSIOClientAuth


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdOSIOClientAuth()

    if cmd.verbose:
        print(cmd, file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # APIAuth...
    api_auth = APIAuth.load(Host)

    if api_auth is None:
        print("APIAuth not available.", file=sys.stderr)
        exit(1)

    if cmd.verbose:
        print(api_auth, file=sys.stderr)

    # User manager...
    user_manager = UserManager(HTTPClient(), api_auth.api_key)

    # Device manager...
    device_manager = DeviceManager(HTTPClient(), api_auth.api_key)

    # check for existing registration...
    device = device_manager.find_for_name(api_auth.org_id, Host.name())

    # check for existing ClientAuth...
    client_auth = ClientAuth.load(Host)


    # ----------------------------------------------------------------------------------------------------------------
    # clean non-matching records...

    if device and client_auth:
        if device.client_id != client_auth.client_id:
            ClientAuth.delete(Host)
            client_auth = None


    # ----------------------------------------------------------------------------------------------------------------
    # validate...

    if device is None or client_auth is None:
        if cmd.set() and not cmd.is_complete():
            print("No device is registered. osio_host_client must therefore set a user:", file=sys.stderr)
            cmd.print_help(sys.stderr)
            exit(1)

        if not cmd.set():
            exit(0)


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    if cmd.set():
        # User...
        if cmd.user_id:
            user = user_manager.find_public(cmd.user_id)

            if user is None:
                print("User not available.", file=sys.stderr)
                exit(1)

        # tags...
        tags = ProjectClient.tags()

        if device and client_auth:
            if cmd.user_id:
                print("Device owner-id cannot be updated.", file=sys.stderr)
                exit(1)

            # update Device...
            updated = ProjectClient.update(device, cmd.description, tags)
            device_manager.update(api_auth.org_id, device.client_id, updated)

            # find updated device...
            device = device_manager.find(api_auth.org_id, device.client_id)

        else:
            # create Device...
            device = ProjectClient.create(Host.name(), api_auth, cmd.description, tags)
            device = device_manager.create(cmd.user_id, device)

            # create ClientAuth...
            client_auth = ClientAuth(cmd.user_id, device.client_id, device.password)

            client_auth.save(Host)

    else:
        # find ClientAuth...
        client_auth = ClientAuth.load(Host)


    if cmd.verbose:
        print(device, file=sys.stderr)

    print(JSONify.dumps(client_auth))
