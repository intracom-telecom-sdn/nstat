#! /usr/bin/python

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""With this module re start the REST Mininet server, that manages a Mininet
topology"""

import argparse
import bottle
import json
import logging

from LinearTopo import Linear
from MeshTopo import Mesh
from DisconnectedTopo import Disconnected

# We must define logging level separately because this module runs
# independently.
logging.basicConfig(level=logging.INFO)

MININET_TOPO = None

@bottle.route('/init/controller/<ip_address>/port/<port>/topology/<topo>/size/<size>/group/<group>/delay/<delay>/hosts/<hosts>', method='POST')
def init(ip_address, port, topo, size, group, delay, hosts):
    """
    Initializes a new topology object. The type of the new topology is
    defined by the topo parameter.

    :param ip_address: controller IP address
    :param port: controller OF port number
    :param topo: type of the topology we want to start ("Disconnected",
    "Linear", "Mesh")
    :param size: initial number of switches to boot the topology with
    :param group: group addition size
    :paran delay: group addition delay (in milliseconds)
    :param hosts: number of hosts per switch.
    :type ip_address: str
    :type port: int
    :type topo: str
    :type size: int
    :type group: int
    :type delay: int
    :param hosts: int
    """

    global MININET_TOPO
    MININET_TOPO = eval(topo)(ip_address, int(port), int(size), int(group),
                              int(delay), int(hosts))
    MININET_TOPO.init_topology()

@bottle.route('/start', method='POST')
def start():
    """
    Calls the start_topology() method of the current topology object to start the
    switches of the topology.
    """
    MININET_TOPO.start_topology()

@bottle.route('/add_switches/<num_switches>', method='POST')
def add_switches(num_switches):
    """
    Calls the add_switches() method of the current topology object to add
    switches to the topology.

    :param num_switches: the number of switches to add to the topology.
    :type num_switches: int
    """

    global MININET_TOPO
    MININET_TOPO.add_switches(int(num_switches))

@bottle.route('/remove_switches/<num_switches>', method='POST')
def remove_switches(num_switches):
    """
    Calls the remove_switches() method of the current topology object to remove
    switches from the topology.

    :param num_switches: the number of switches to remove
    :type num_switches: int
    """

    global MININET_TOPO
    MININET_TOPO.remove_switches(int(num_switches))


@bottle.route('/get_switches', method='POST')
def get_switches():
    """
    Calls the get_switches() method of the current topology object to query the
    current number of switches.

    :returns: number of switches of the topology
    :rtype: int
    """

    global MININET_TOPO
    return json.dumps(MININET_TOPO.get_switches())

@bottle.route('/stop', method='POST')
def stop():
    """
    Calls the stop_topology() method of the current topology object to terminate the
    topology.
    """

    global MININET_TOPO
    MININET_TOPO.stop_topology()

@bottle.route('/ping_all', method='POST')
def ping_all():
    """
    Calls the ping_all() method of the current topology object to issue
    all-to-all ping commands
    """

    global MININET_TOPO
    MININET_TOPO.ping_all()

def rest_start():
    """Starts Mininet REST server"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--rest-host',
                        required=True,
                        type=str,
                        dest='rest_host',
                        action='store',
                        help='IP address to start Mininet REST server')
    parser.add_argument('--rest-port',
                        required=True,
                        type=str,
                        dest='rest_port',
                        action='store',
                        help='Port number to start Mininet REST server')
    args = parser.parse_args()

    bottle.run(host=args.rest_host, port=args.rest_port, debug=True)

if __name__ == '__main__':
    rest_start()
