# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Mininet-related utilities
"""

import common
import logging
import multiprocessing
import time
import util.customsubprocess
import util.netutil
import util.process



def copy_mininet_handlers(mininet_node, mininet_dir_source, mininet_dir_target):
    """
    Copies Mininet handlers on the remote Mininet node

    :param mininet_node:  named tuple with all connection information. ['name',
    'ip', 'ssh_port', 'username', 'password']
    :param mininet_dir_source: directory path from local machine to copy, full
    location required
    :param mininet_dir_target: remote destination, full location required
    :type mininet_node: str
    :type mininet_dir_source: str
    :type mininet_dir_target: str
    """

    util.netutil.copy_dir_local_to_remote(mininet_node, mininet_dir_source,
                                          mininet_dir_target)

def delete_mininet_handlers(mininet_node, mininet_folder):
    """
    Removes Mininet handlers from the remote Mininet node

    :param mininet_node: a named tuple with all the connection information.
    It must have the following elements: ['name', 'ip', 'ssh_port', 'username',
    'password']
    :param mininet_folder: full of mininet folder (containing mininet handlers)
    to be removed
    :type mininet_node: namedtuple<str,str,str,str,str>
    :type mininet_folder: str
    """

    util.netutil.remove_remote_directory(mininet_node, mininet_folder)


def init_mininet_topo(mininet_init_topo_handler, mininet_rest_server,
                      controller_ip, controller_port, mininet_topology_type,
                      mininet_size, mininet_group_size, mininet_group_delay_ms,
                      mininet_hosts_per_switch):
    """
    Locally calls the Mininet handler that remotely initializes a topology on
    a remote Mininet node

    :param mininet_init_topo_handler: full path of the handler to initialize
    the Mininet topology
    :param mininet_rest_server: named tuple containng 1) mininet_node_ip
    2)mininet_rest_server_port the REST server listens to
    :param controller_ip: controller IP
    :param controller_port: controller OpenFlow port
    :param mininet_topology_type: Type of the network topology. It can have
    one of the following values (DisconnectedTopo,LinearTopo or MeshTopo)
    :param mininet_size: size of the Mininet tpology
    :param mininet_group_size: size of Mininet group (batches of switches)
    :param mininet_group_delay_ms: delay in which Mininet groups are
    initialized
    :param mininet_hosts_per_switch: number of hosts each Mininet switch is
    attached to
    :type mininet_init_topo_handler: str
    :type mininet_rest_server: namedtuple<str,int>
    :type controller_ip: str
    :type controller_port: int
    :type mininet_topology_type: str
    :type mininet_size: int
    :type mininet_group_size: int
    :type mininet_group_delay_ms: int
    :type mininet_hosts_per_switch: int
    """

    init_topo_command = [mininet_init_topo_handler, mininet_rest_server.ip,
                          str(mininet_rest_server.port), controller_ip,
                          str(controller_port), str(mininet_topology_type),
                          str(mininet_size), str(mininet_group_size),
                          str(mininet_group_delay_ms),
                          str(mininet_hosts_per_switch)]
    util.customsubprocess.check_output_streaming(init_topo_command,
        '[init_mininet_topo] Topology type: {0}'.
        format(mininet_topology_type))


def mininet_topo_check_booted(expected_switches, mininet_group_size,
                              mininet_group_delay_ms,
                              mininet_get_switches_handler,
                              mininet_rest_server,
                              controller_nb_interface, num_tries=3):
    """
    Check if a Mininet topology has been booted. Check both from the Mininet
    side and from the controller operational DS.

    :param expected_switches: expected Mininet switches
    :param mininet_group_size: group size at which switches are added in a
    Mininet topo
    :param mininet_group_delay_ms: delay between group additions
    (in milliseconds)
    :param mininet_get_switches_handler: Mininet handler used to query the
    current number of switches in a Mininet topology
    :param mininet_rest_server: named tuple containing 1) mininet_node_ip
    2)mininet_rest_server_port the REST server listens to
    :param controller_nb_interface: named tuple containing 1) controller_node_ip
    2) controller_restconf_port 3) controller_restconf_user
    4) controller_restconf_password
    :param num_tries: maximum number of tries until the method identifies that
    number of discovered switches of the Mininet topology is equal to the
    number of expected Mininet switches
    :raises Exception: if we reach max number of tries and either the
    controller has not seen the topology or the topology has failed to start.
    :type expected_switches: int
    :type mininet_group_size: int
    :type mininet_group_delay_ms: int
    :type mininet_get_switches_handler: str
    :type mininet_rest_server: namedtuple<str,int>
    :type controller_nb_interface: namedtuple<str,int,str,str>
    :type num_tries: int
    """

    mininet_group_delay = float(mininet_group_delay_ms)/1000
    discovered_switches = 0
    ds_switches = 0
    tries = 0

    while tries < num_tries:
        logging.info('[mininet_topo_check_booted] Check if topology is up.')

        # Here we sleep in order to give time to the controller to discover
        # topology through the LLDP protocol.
        time.sleep(int(expected_switches/mininet_group_size) * \
                   mininet_group_delay + 15)
        outq = multiprocessing.Queue()

        try:
            util.customsubprocess.check_output_streaming(
                [mininet_get_switches_handler, mininet_rest_server.ip,
                 str(mininet_rest_server.port)],
                '[mininet_get_switches_handler]', queue=outq)
            discovered_switches = int(outq.get().strip())
            logging.info('[mininet_topo_check_booted] Discovered {0} switches'
                          ' at the Mininet side'.format(discovered_switches))

            ds_switches = common.check_ds_switches(controller_nb_interface)
            logging.info('[mininet_topo_check_booted] Discovered {0} switches'
                          ' at the controller side'.format(ds_switches))
            if discovered_switches == expected_switches and \
                ds_switches == expected_switches and expected_switches != 0:
                return

        except:
            pass

        tries += 1

    raise Exception('Topology did not fully initialize. Expected {0} '
                    'switches, but found {1} at the Mininet side and {2} '
                    'at the controller side.'.
                    format(expected_switches, discovered_switches,ds_switches))


def start_mininet_server(mininet_ssh_session, mininet_server_remote_path,
                         mininet_rest_server):
    """
    Remotely boots a REST server on the Mininet node over an SSH connection

    :param mininet_ssh_session: ssh session used to issue remote command
    :param mininet_server_remote_path: path where mininet_custom_boot.py is
    stored and used to start the Mininet topology.
    :param mininet_rest_server: named tuple containing 1) mininet_node_ip
    2)mininet_rest_server_port the REST server listens to
    :raises Exception: if getpid_listeningonport() returns -1, Mininet rest
    server failed to start
    :type mininet_ssh_session: ssh connection object
    :type mininet_server_remote_path: str
    :type mininet_rest_server: namedtuple<str,int>
    """

    boot_command = ('sudo python {0} --rest-host {1} --rest-port {2}'.
                    format(mininet_server_remote_path, mininet_rest_server.ip,
                           mininet_rest_server.port))
    util.netutil.ssh_run_command(mininet_ssh_session, boot_command,
                                 prefix='[start_mininet_server]',
                                 lines_queue=None, print_flag=True,
                                 block_flag=False)
    logging.debug('{0} {1}'.format('[start_mininet_server] boot command: ',
                                   boot_command))
    num_of_tries = 10
    mininet_server_pid = -1
    logging.info('{0} Wait until mininet REST server is up and running.'.
                 format('[start_mininet_server] '))
    while (mininet_server_pid == -1) and (num_of_tries > 0):
        mininet_server_pid = util.process.getpid_listeningonport(
            mininet_rest_server.port, mininet_ssh_session)
        time.sleep(1)
        num_of_tries -= 1

    if mininet_server_pid == -1:
        logging.error('{0} Fail to start mininet REST server.'.
                      format('[start_mininet_server]'))
        raise Exception('Failed to start mininet REST server. Got invalid pid.')

def start_stop_mininet_topo(mininet_start_stop_handler, mininet_rest_server,
                       mininet_action):
    """
    Locally calls the Mininet handler that remotely starts an initialized
    topology on a remote Mininet node

    :param mininet_start_stop_handler: full path of the handler to start the
    Mininet topology
    :param mininet_rest_server: named tuple containing the ip address of
    mininet REST server and the port it listens for requests
    :param mininet_action: defines the operation that start/stop mininet
    handler will perform. Can have either 'start' or 'stop' value.
    :type mininet_start_stop_handler: str
    :type mininet_rest_server: namedtuple<str,int>
    :type mininet_action: str
    """

    util.customsubprocess.check_output_streaming(
        [mininet_start_stop_handler, mininet_rest_server.ip,
        str(mininet_rest_server.port), mininet_action],
        '[mininet_start_stop_handler]')
    logging.info('[mininet_start_stop_handler] {0} mininet topology.'.
                 format(mininet_action))


def stop_mininet_server(mininet_ssh_session, mininet_rest_server_port):
    """
    Remotely stops the REST server on the Mininet node

    :param mininet_ssh_session: ssh session used to issue remote command
    :param mininet_rest_server_port: port the REST server listens to
    :type test_type: ssh connection object
    :type mininet_rest_server_port: int
    """

    get_pid_cmd = """sudo netstat -antup --numeric-ports | grep ':""" + \
                  str(mininet_rest_server_port) + \
                  """ ' | awk '{print $NF}' | awk -F '/' '{print $1}'"""

    cmd_output = util.netutil.ssh_run_command(
        mininet_ssh_session, get_pid_cmd, prefix='[stop_mininet_server]')[1]

    mininet_server_pid = cmd_output.strip()
    mininet_server_pid = mininet_server_pid.strip('-')
    util.netutil.ssh_run_command(mininet_ssh_session,
        'sudo kill -9 {0}'.format(mininet_server_pid),
        prefix='[stop_mininet_server]')
    util.netutil.ssh_run_command(mininet_ssh_session, 'sudo mn -c',
        prefix='[stop_mininet_server]')
    mininet_server_pid = util.process.getpid_listeningonport(
            mininet_rest_server_port, mininet_ssh_session)
    if mininet_server_pid != -1:
        logging.error('{0} Fail to stop mininet REST server.'.
                      format('[stop_mininet_server]'))
        raise Exception('Fail to stop mininet REST server. Got invalid pid.')

