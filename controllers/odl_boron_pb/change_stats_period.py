#! /usr/bin/env python3.4

"""Handler changing the rate of statistics collection from the topology
switches
"""

import json
import requests
import sys


CONTROLLER_DIR_NAME = 'distribution-karaf-0.5.0-Boron'


def change_stats_period():
    """
    Takes as command line argument the string as a command line argument
    <controller_ip>:<controller_sb_port>:<controller_auth_username>:<controller_auth_pass>
    and disables statistic collection from controller.
    """
    conn_attributes = str(sys.argv[1]).split(':')
    url = ('http://{0}:{1}/restconf/operations/statistics-manager-control:'
           'change-statistics-work-mode'.format(conn_attributes[0],
                                                conn_attributes[1]))
    auth = (conn_attributes[2], conn_attributes[3])
    headers = {'content-type': 'application/json'}
    if conn_attributes[4] == 'enable':
        data = {'input': {'mode': 'COLLECT_ALL'}}
    else:
        data = {'input': {'mode': 'FULLY_DISABLED'}}
    r = requests.post(url, data=json.dumps(data), headers=headers, auth=auth)
    if r.status_code == 200:
        sys.exit(0)
    else:
        sys.exit(r.status_code)

if __name__ == '__main__':
    change_stats_period()
