# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Mininet-related utilities
"""

import logging
import time
import util.customsubprocess
import util.netutil

def start_mininet_server(mininet_ssh_session, mininet_server_remote_path,
                         mininet_rest_server_host, mininet_rest_server_port):
    """
    Remotely boots a REST server on the Mininet node over an SSH connection

    :param mininet_ssh_session: ssh session used to issue remote command
    :param mininet_server_remote_path: path where mininet_custom_boot.py is
    stored and used to start the Mininet topology.
    :param mininet_rest_server_host: hostname/IP the REST server should listen
    to
    :param mininet_rest_server_port: port the REST server should listen to
    :type mininet_ssh_session: ssh connection object
    :type mininet_server_remote_path: str
    :type mininet_rest_server_host: str
    :type mininet_rest_server_port: int
    """

    boot_command = ('sudo python {0} --rest-host {1} --rest-port {2}'.
                    format(mininet_server_remote_path, mininet_rest_server_host,
                           mininet_rest_server_port))
    util.netutil.ssh_run_command(mininet_ssh_session, boot_command,
                                 prefix='[start_mininet_server]',
                                 lines_queue=None, print_flag=True,
                                 block_flag=False)

    logging.info('{0} {1}'.format('[start_mininet_server] boot command: ',
                                   boot_command))
    time.sleep(10)

def init_mininet_topo(mininet_init_topo_handler, mininet_rest_server_host,
                       mininet_rest_server_port, controller_ip,
                       controller_port, mininet_topology_type, mininet_size,
                       mininet_group_size, mininet_group_delay_ms,
                       mininet_hosts_per_switch):
    """
    Locally calls the Mininet handler that remotely initializes a topology on
    a remote Mininet node

    :param mininet_init_topo_handler: full path of the handler to initialize
    the Mininet topology
    :param mininet_rest_server_host: hostname/IP the REST server listens to
    :param mininet_rest_server_port: port the REST server listens to
    :param controller_ip: controller IP
    :param controller_port: controller OpenFlow port
    :param mininet_topology_type: Type of the network topology. It can have
    one of the following values (DisconnectedTopo,LinearTopo or MeshTopo)
    :param mininet_size: Size of the Mininet tpology
    :param mininet_group_size: Size of the Mininet Group
    :param mininet_group_delay_ms: Delay in which Mininet groups are
    initialized
    :param mininet_hosts_per_switch: Number of Hosts each Mininet switch is
    attached to
    :type mininet_init_topo_handler: str
    :type mininet_rest_server_host: str
    :type mininet_rest_server_port: int
    :type controller_ip: str
    :type controller_port: int
    :type Topology: str
    :type mininet_size: int
    :type mininet_group_size: int
    :type mininet_group_delay: int
    :type mininet_hosts_per_switch: int
    :type start_topo_command: list<str>
    """

    init_topo_command = [mininet_init_topo_handler, mininet_rest_server_host,
                          str(mininet_rest_server_port), controller_ip,
                          str(controller_port), str(mininet_topology_type),
                          str(mininet_size), str(mininet_group_size),
                          str(mininet_group_delay_ms),
                          str(mininet_hosts_per_switch)]
    util.customsubprocess.check_output_streaming(init_topo_command,
        '[init_mininet_topo] Topology type: {0}'.
        format(mininet_topology_type))


def start_mininet_topo(mininet_start_handler, mininet_rest_server_host,
                      mininet_rest_server_port):
    """
    Locally calls the Mininet handler that remotely starts an initialized
    topology on a remote Mininet node

    :param mininet_start_handler: full path of the handler to start the Mininet
    topology
    :param mininet_rest_server_host: hostname/IP the REST server listens to
    :param mininet_rest_server_port: port the REST server listens to
    :type mininet_start_handler: str
    :type mininet_rest_server_host: str
    :type mininet_rest_server_port: int
    """

    util.customsubprocess.check_output_streaming(
        [mininet_start_handler, mininet_rest_server_host,
        str(mininet_rest_server_port)], '[mininet_start_handler]')


def stop_mininet_topo(mininet_stop_handler, mininet_rest_server_host,
                      mininet_rest_server_port):
    """
    Locally calls the Mininet handler that remotely stops a topology on a
    remote Mininet node

    :param mininet_stop_handler: full path of the handler to stop the Mininet
    topology
    :param mininet_rest_server_host: hostname/IP the REST server listens to
    :param mininet_rest_server_port: port the REST server listens to
    :type mininet_stop_handler: str
    :type mininet_rest_server_host: str
    :type mininet_rest_server_port: int
    """

    util.customsubprocess.check_output_streaming(
        [mininet_stop_handler, mininet_rest_server_host,
        str(mininet_rest_server_port)], '[mininet_stop_handler]')


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

    cmd_exit_status, cmd_output = util.netutil.ssh_run_command(
        mininet_ssh_session, get_pid_cmd, prefix='[stop_mininet_server]')

    mininet_server_pid = cmd_output.strip()
    mininet_server_pid = mininet_server_pid.strip('-')
    util.netutil.ssh_run_command(mininet_ssh_session,
        'sudo kill -9 {0}'.format(mininet_server_pid),
        prefix='[stop_mininet_server]')
    util.netutil.ssh_run_command(mininet_ssh_session, 'sudo mn -c',
        prefix='[stop_mininet_server]')


def delete_mininet_handlers(mininet_ssh_server_ip, mininet_user, mininet_pass,
                            mininet_folder, remote_port=22):
    """
    Cleans up Mininet handlers on the remote Mininet node

    :param mininet_ssh_server_ip: IP address of the ssh server on the Mininet
    node
    :param mininet_user: username for the Mininet node
    :param mininet_pass: password for the Mininet node
    :param mininet_folder: folder with Mininet handlers
    :param remote_port: port for mininet_ssh_server_ip
    :type mininet_ssh_server_ip: str
    :type mininet_user: str
    :type mininet_pass: str
    :type mininet_folder: str
    :type remote_port: int
    """

    util.netutil.remove_remote_directory(mininet_ssh_server_ip, mininet_user,
                                         mininet_pass, mininet_folder,
                                         remote_port)

def copy_mininet_handlers(mininet_ssh_server_ip, mininet_user, mininet_pass,
                          mininet_source, mininet_target, remote_port=22):
    """
    Copies Mininet handlers on the remote Mininet node

    :param mininet_ssh_server_ip: IP address of the ssh server on the Mininet
    node
    :param mininet_user: username for the Mininet node
    :param mininet_pass: password for the Mininet node
    :param mininet_source: folder with Mininet handlers
    :param mininet_target: folder where Mininet handlers will be copied
    :param remote_port: port for mininet_ssh_server_ip
    :type mininet_ssh_server_ip: str
    :type mininet_user: str
    :type mininet_pass: str
    :type mininet_folder: str
    :type remote_port: int
    """

    util.netutil.copy_directory_to_target(mininet_ssh_server_ip, mininet_user,
                                          mininet_pass, mininet_source,
                                          mininet_target, remote_port)
