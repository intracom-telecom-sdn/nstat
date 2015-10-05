#! /usr/bin/env python3.4

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html


"""
Handler for requesting a Mininet REST server to initialize a Mininet topology
on the current node
"""

import requests
import sys

def init_topology_main():
    """ 
    Command line arguments:

    1. IP address of the Mininet REST server
    2. Port number of the Mininet REST server
    3. IP address of the controller
    4. OF port number of the controller
    5. Mininet topology type
    6. Mininet topology size
    7. Mininet group size
    8. Mininet goup delay (in milliseconds)
    9. Mininet hosts per switch
    """

    mininet_rest_host = sys.argv[1]
    mininet_rest_port = sys.argv[2]
    controller_ip_address = sys.argv[3]
    controller_of_port = sys.argv[4]
    mininet_topo_type = sys.argv[5]
    mininet_topo_size = sys.argv[6]
    mininet_group_size = sys.argv[7]
    mininet_group_delay = sys.argv[8]
    mininet_hosts_per_switch = sys.argv[9]

    session = requests.Session()
    session.trust_env = False
    url = ('http://{0}:{1}/init/controller/{2}/port/'
           '{3}/topology/{4}/size/{5}/group/{6}/delay/{7}/hosts/{8}'.
           format(mininet_rest_host, mininet_rest_port, controller_ip_address,
                  controller_of_port, mininet_topo_type, mininet_topo_size,
                  mininet_group_size, mininet_group_delay,
                  mininet_hosts_per_switch))

    print('[init_topology_handler][url] {0}'.format(url))

    init_topology_call = session.post(url)
    print('[init_topology_handler][response status code] {0}'.
                 format(init_topology_call.status_code))
    print('[init_topology_handler][response data] {0}'.
                 format(init_topology_call.text))

    if init_topology_call.status_code != 200:
        sys.exit(init_topology_call.status_code)

if __name__ == '__main__':
    init_topology_main()
