#! /usr/bin/env python3.4

"""
This handler returns the number of links of a topology, connected
to the controller. This information is extracted from controller's operational
datastore, using RESTCONF.
"""

import sys
import logging
import requests


def get_oper_links():
    """
    Query number of links registered in ODL operational DS

    :returns: number of links found, 0 if none exists and -1 in case of \
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
        logging.error('[get_oper_links] Fail response from operational DS')
        return -1
    links = [link for link in datastore.get('link', [])]
    logging.debug('[get_oper_links] Discovered links: {0}'.format(len(links)))
    print(len(links))

if __name__ == '__main__':
    get_oper_links()
