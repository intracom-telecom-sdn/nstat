#! /usr/bin/env python3.4

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Handler for requesting a Mininet REST server to start a Mininet topology on
the current node
"""

import requests
import sys

def northbound_generator():
    """
    Command line arguments:

    1. IP Address of the Mininet REST server
    2. Port number of the Mininet REST server
    """

    mininet_rest_host = sys.argv[1]
    mininet_rest_port = sys.argv[2]

    session = requests.Session()
    session.trust_env = False

    url = 'http://{0}:{1}/start'.format(mininet_rest_host, mininet_rest_port)

    print('[start_topology_handler][url] {0}'.format(url))
    mininet_start_call = session.post(url)
    print('[start_topology_handler][response status code] {0}'.
          format(mininet_start_call.status_code))
    print('[start_topology_handler][response data] {0}'.
          format(mininet_start_call.text))

    if mininet_start_call.status_code != 200:
        sys.exit(mininet_start_call.status_code)
        
        
        
        
flow_master_thread,
                                    args=(mqueue, controller_ip,
                                          str(controller_restconf_port),
                                          total_flows, mininet_size,
                                          flow_workers, f_temp,
                                          flow_operations_delay_ms,
                                          flow_delete_flag,
                                          flow_discovery_deadline_ms,
                                          auth_token)        
        
        

if __name__ == '__main__':
    northbound_generator()
