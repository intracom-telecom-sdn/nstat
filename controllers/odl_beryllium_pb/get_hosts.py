#! /usr/bin/env python3.4

"""
This handler returns the number of hosts of a topology, connected
to the controller. This information is extracted from controller's operational
datastore, using RESTCONF.
"""

import sys
import logging
import requests


def get_oper_hosts():
    """
    Query number of hosts registered in ODL operational DS

    :returns: number of hosts found, 0 if none exists and -1 in case of \
        error.
    :rtype: int
    """
    ip = sys.argv[1]
    port = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(ip, port))
    s = requests.Session()
    s.trust_env = False
    auth_token = (username, password)
    try:
        datastore = s.get(url=url,
                          auth=auth_token).json()['topology'][0]
    except:
        logging.error('[get_oper_hosts] Fail response from operational DS')
        return -1

    hosts = [node for node in datastore.get('node', [])
             if node['node-id'].startswith('host:')]
    logging.debug('[get_oper_hosts] Discovered hosts: {0}'.format(len(hosts)))

    print(len(hosts))

if __name__ == '__main__':
    get_oper_hosts()
