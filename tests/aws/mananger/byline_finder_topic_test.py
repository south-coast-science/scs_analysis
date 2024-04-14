#!/usr/bin/env python3

"""
Created on 10 Apr 2024

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys

from scs_core.aws.manager.byline.byline_finder import BylineFinder

from scs_core.aws.security.cognito_client_credentials import CognitoClientCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_host.sys.host import Host


# ------------------------------------------------------------------------------------------------------------
# authentication...

credentials = CognitoClientCredentials.load_for_user(Host, name='super')

if not credentials:
    exit(1)

gatekeeper = CognitoLoginManager()
auth = gatekeeper.user_login(credentials)

if not auth.is_ok():
    print("login: %s." % auth.authentication_status.description, file=sys.stderr)
    exit(1)


# --------------------------------------------------------------------------------------------------------------------

finder = BylineFinder()
print(finder)

topics = finder.find_topics(auth.id_token)

for topic in topics:
    print(topic)

print("len: %s" % len(topics))

