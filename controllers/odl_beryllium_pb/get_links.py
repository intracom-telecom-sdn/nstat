#! /usr/bin/env python3.4
import sys
import logging

def get_oper_links():
    """Query number of links registered in ODL operational DS

    :returns: number of links found, 0 if none exists and -1 in case of
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
        logging.error('[get_oper_links] Fail getting response from operational datastore')
        return -1
    links = [link for link in datastore.get('link', [])]
    logging.debug('[get_oper_links] Discovered links: {0}'.format(len(links)))
    return len(links)

if __name__ == '__main__':
    get_oper_links()