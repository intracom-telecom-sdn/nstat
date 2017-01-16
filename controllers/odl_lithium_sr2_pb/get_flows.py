#! /usr/bin/env python3.4

"""
This handler returns the number of installed flows of a topology, connected
to the controller. This information is extracted from controller's operational
datastore, using RESTCONF.
"""

import json
import re
import requests
import sys


def get_oper_flows():
    """
    Query number of flows registered in ODL operational DS

    :returns: number of flows found, 0 if none exists and -1 in case of \
        error.
    :rtype: int
    """

    ip = sys.argv[1]
    port = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]
    flows_found = get_flow_stats(ip, port, username, password)
    print(flows_found)


def get_flow_stats(ip, port, username, password):
    """
    Collects and returns data about installed flows for the topology nodes

    :param ip: controller IP Address
    :param port: controller restconf port number
    :param username: username for restconf authorization
    :param password: password for restconf authorization
    :returns: the number of installed flows in the topology nodes \
        or a negative number in a negative case
    :rtype: int
    :type ip: str
    :type port: int
    :type username: str
    :type password: str
    """
    url = ('http://{0}:{1}/restconf/operational/opendaylight'
    '-inventory:nodes'.format(ip, port))
    headers = {'Accept': 'application/json'}
    found_flows = 0
    s = requests.Session()
    s.trust_env = False
    auth_token = (username, password)
    try:
        req = s.get(url, headers=headers, stream=False, auth=auth_token)
        str_response = req.content.decode('utf-8')
    except:
        found_flows = 0
        return -1
    if req.status_code == 200:
        try:
            nodes = json.loads(str_response)['nodes']['node']
            switches = []
            for node in nodes:
                if re.search('openflow', node['id']) is not None:
                    switches.append(node)
            switches = sorted(
                switches,
                key=lambda k: int(
                    re.findall(
                        '\d+',
                        k['id'])[0]))
            for switch in switches:
                try:
                    tables = switch['flow-node-inventory:table']

                    for table in tables:
                        try:
                            found_flows += len(table['flow'])
                        except KeyError:
                            pass
                except KeyError:
                    return -2
        except KeyError:
            return -3
    else:
        return -4
    s.close()
    return found_flows

if __name__ == '__main__':
    get_oper_flows()
