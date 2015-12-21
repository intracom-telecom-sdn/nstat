#! /usr/bin/env python3.4

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Handler for requesting a Mininet REST server to stop a Mininet topology on
the current node
"""

import requests
import sys

def mininet_start_stop_main():
    """
    Command line arguments:

    1. IP Address of the Mininet REST server
    2. Port number of the Mininet REST server
    3. Action can have value of 'start' or 'stop'
    """

    mininet_rest_host = sys.argv[1]
    mininet_rest_port = sys.argv[2]
    mininet_action = sys.argv[3]

    if mininet_action != 'start' and mininet_action != 'stop':
        print('Mininet action {0} was not valid.'.format(mininet_action))
        sys.exit(1)

    session = requests.Session()
    session.trust_env = False

    url = 'http://{0}:{1}/{2}'.format(mininet_rest_host, mininet_rest_port,
                                      mininet_action)

    print('[{0}_topology_handler][url] {1}'.format(mininet_action, url))
    mininet_stop_call = session.post(url)
    print('[{0}_topology_handler][response status code] {1}'.
          format(mininet_action, mininet_stop_call.status_code))
    print('[{0}_topology_handler][response data] {1}'.
          format(mininet_action, mininet_stop_call.text))

    if mininet_stop_call.status_code != 200:
        sys.exit(mininet_stop_call.status_code)

if __name__ == '__main__':
    mininet_start_stop_main()
