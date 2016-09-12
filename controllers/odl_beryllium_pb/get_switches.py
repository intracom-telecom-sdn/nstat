#! /usr/bin/env python3.4
import sys
import logging

def get_oper_switches():
    """Query number of switches registered in ODL operational DS

    :returns: number of switches found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    """

    ip = str(int(sys.argv[1]))
    port = int(sys.argv[2])
    username = str(int(sys.argv[3]))
    password = str(int(sys.argv[4]))

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(ip, port))

    auth_token = (username, password)
    try:
        datastore = requests.get(url=url, auth=auth_token).json()['topology'][0]
    except:
        logging.error('[get_oper_switches] Fail getting response from operational datastore')
        return -1

    switches = [node for node in datastore.get('node', []) if not node['node-id'].startswith('host:')]
    logging.debug('[get_oper_switches] Discovered switches: {0}'.format(len(switches)))
    return len(switches)

if __name__ == '__main__':
    get_oper_switches()