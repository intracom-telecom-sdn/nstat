#! /usr/bin/env python3.4
import sys

def get_oper_hosts():
    """Query number of hosts registered in ODL operational DS

    :returns: number of hosts found, 0 if none exists and -1 in case of
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
        logging.error('[get_oper_hosts] Fail getting response from operational datastore')
        return -1

    hosts = [node for node in datastore.get('node', []) if node['node-id'].startswith('host:')]
    logging.debug('[get_oper_hosts] Discovered hosts: {0}'.format(len(hosts)))
    return len(hosts)

if __name__ == '__main__':
    get_oper_hosts()

