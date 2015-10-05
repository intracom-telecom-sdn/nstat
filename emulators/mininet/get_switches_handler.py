#! /usr/bin/env python3.4

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Handler for querying a Mininet REST server for the number of switches in the
Mininet topology of the current node
"""

import requests
import sys

def get_switches():
    """ 
    Command line arguments: 

    1. IP address of the Mininet REST server
    2. Port number of the Mininet REST server

    It returns on the console standard output the current number of switches
    of the topology
    """

    mininet_rest_host = sys.argv[1]
    mininet_rest_port = sys.argv[2]
    session = requests.Session()
    session.trust_env = False
    url = 'http://{0}:{1}/get_switches'.format(mininet_rest_host,
                                               mininet_rest_port)

    get_switches_call = session.post(url)
    print(get_switches_call.text)

if __name__ == '__main__':
    get_switches()
