# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Support for customized booting of Mininet topologies"""

import logging
import time
import socket
import struct
import mininet

from mininet import node, link
from mininet.util import fixLimits

logging.basicConfig(level=logging.INFO)

class CustomBootedTopo(object):
    """
    Superclass representing a Mininet topology that is being booted in custom
    way. Switches are being added in groups with certain delay between each
    group.
    """

    def __init__(self, controller_ip, controller_port, switches, group_size,
                 group_delay_ms, hosts_per_switch):
        """
        :param controller_ip: controller's ip address
        :param controller_port: controller's OF port number
        :param switches: the number of switches of the topology
        :param group_size: the number of switches in each addition group
        :param group_delay_ms: the delay between each addition group
        (in milliseconds)
        :param hosts_per_switch: number of hosts per switch.
        :type controller_ip: str
        :type controller_port: int
        :type switches: int
        :type group_size: int
        :type group_delay: int
        :type hosts_per_switch: int
        """

        self._switches = []
        self._init_switches = switches
        self._curr_switches = 0
        self._dpid_offset = 0
        self._group_size = group_size
        self._group_delay = float(group_delay_ms)/1000
        self._hosts_per_switch = hosts_per_switch
        # the first assigned mac address for hosts
        self._host_base_mac = 0x1a0000000001
        # the first assigned IP adderss for hosts
        self._host_next_ip = 0x0a000002

        self._controller_ip = controller_ip
        self._controller_port = controller_port
        # maps a switch of the topology to its owned hosts
        self._switch_hosts = {}
        # maps a switch to its neighboring links
        self._switch_links = {}
        # controller object where the topology will conect
        self._controller = node.RemoteController(name='c0',
                                                 ip=controller_ip,
                                                 port=controller_port)
        fixLimits()

    def init_topology(self):
        """Inits the topology"""

        logging.info("[mininet] Initializing topology.")
        self.add_switches(self._init_switches, startflg=False)
        logging.info('[mininet] Topology initialized successfully. '
                     'Booted up {0} switches'.format(self._init_switches))

    def start_topology(self):
        """Starts the topology"""

        logging.info("[mininet] Starting switches and topology.")
        for ind in range(0, self._curr_switches):
            if ind % self._group_size == 0:
                time.sleep(self._group_delay)
            logging.debug('[mininet] Starting switch with index {0}'.
                          format(ind + 1))
            self._switches[ind].start([self._controller])

        logging.info('[mininet] Topology started successfully. '
                     'Booted up {0} switches'.format(self._curr_switches))

    def get_switches(self):
        """Returns the total number of switches of the topology

        :returns: number of switches of the topology
        :rtype: int
        """

        return self._curr_switches


    def stop_topology(self):
        """Stops the topology"""

        logging.info('[mininet] Destroying topology. Terminating switches.')
        self.remove_switches(self._curr_switches)
        logging.info('[mininet] Topology terminated successfully')


    def add_switches(self, switches_to_add, startflg=True):
        """Adds switches to the topology

        :param: switches_to_add: number of switches to be added
        :param: startflg: if True the newly added switch is started so that its
        link with the rest of the switches within the topology becomes active.
        :type: switches_to_add: int
        :type: startflg: bool
        """

        for ind in range(1, switches_to_add+1):
            switch_name = 's' + \
                str(self._dpid_offset + self._curr_switches + ind)
            logging.debug('[mininet] Creating switch {0}'.format(switch_name))
            switch = node.OVSSwitch(switch_name, inNamespace=False,
                                    protocols='OpenFlow13')
            self._add_hosts_to_switch(switch)

            if self._switches:
                self._add_links_to_switch(switch, startflg)
            logging.debug(
                '[mininet] Adding {0} in topology list'.format(switch_name))

            if startflg:
                switch.start([self._controller])
            self._switches.append(switch)

        logging.info('[mininet] {0} switches started successfully.'.
                     format(switches_to_add))

        self._curr_switches += switches_to_add

    def remove_switches(self, switches_to_remove):
        """Removes switches objects equal to "switches_to_remove" from the
        current topology. _switch_hosts, _switch_links dictionaries
        are also updated when a switch is removed.

        :param: switches_to_remove: the number of switches to remove from the
        topology
        :type: switches_to_remove: int
        """

        if switches_to_remove > self._curr_switches:
            switches_to_remove = self._curr_switches

        switches_slice_to_stop = self._switches[-switches_to_remove:]
        self._switches = self._switches[:-switches_to_remove]

        for switch in switches_slice_to_stop:
            logging.debug(
                '[mininet] Removing switch {0}.'.format(switch.name))
            self._remove_links_from_switch(switch)
            self._remove_hosts_from_switch(switch)
            switch.stop()
            del switch

        self._curr_switches -= switches_to_remove

    def _add_hosts_to_switch(self, switch):
        """Connects a switch to its specified number of hosts

        :param: switch: Mininet switch
        :type switch: node.OVSSwitch
        """

        hosts = []
        for ind in range(self._hosts_per_switch):
            host = node.Host('h_' + str(ind) + '_' + switch.name)
            link.Link(host, switch)
            host.setIP(
                socket.inet_ntoa(struct.pack('>I', self._host_next_ip)) + '/8')
            host.setMAC(':'.join(''.join(pair)
                            for pair in zip(*[iter(hex(self._host_base_mac + self._host_next_ip))]*2)))

            self._host_next_ip += 1
            hosts.append(host)

        self._switch_hosts[switch] = hosts

    def _remove_hosts_from_switch(self, switch):
        """
        Removes an element (a list of hosts) from the _switch_hosts map

        :param: switch: the switch whose list of hosts we want to remove
        :type switch: node.OVSSwitch
        """

        self._host_next_ip -= self._hosts_per_switch
        for host in self._switch_hosts[switch]:
            host.stop()
        del self._switch_hosts[switch]

    def _remove_links_from_switch(self, switch):
        """
        Removes an element (list of links) from the _switch_links map

        :param: switch: the switch whose list of links we want to remove
        :type switch: node.OVSSwitch
        """

        del self._switch_links[switch]

    def ping_all(self):
        """
        All-to-all host pinging used for testing.
        """

        for switches1, hosts1 in list(self._switch_hosts.items()):
            for current_host1 in hosts1:
                for switches2, hosts2 in list(self._switch_hosts.items()):
                    for current_host2 in hosts2:
                        if current_host1.name != current_host2.name:
                            ping_message = current_host1.cmd(
                                                'ping -c1', current_host2.IP())
                            logging.debug(
                                '[Mininet] Ping all message: {0}'.
                                format(ping_message))
