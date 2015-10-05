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

def mininet_stop_main():
    """ 
    Command line arguments:

    1. IP Address of the Mininet REST server
    2. Port number of the Mininet REST server
    """

    mininet_rest_host = sys.argv[1]
    mininet_rest_port = sys.argv[2]

    session = requests.Session()
    session.trust_env = False

    url = 'http://{0}:{1}/stop'.format(mininet_rest_host, mininet_rest_port)

    print('[stop_topology_handler][url] {0}'.format(url))
    mininet_stop_call = session.post(url)
    print('[stop_topology_handler][response status code] {0}'.
          format(mininet_stop_call.status_code))
    print('[stop_topology_handler][response data] {0}'.
          format(mininet_stop_call.text))

    if mininet_stop_call.status_code != 200:
        sys.exit(mininet_stop_call.status_code)

if __name__ == '__main__':
    mininet_stop_main()
