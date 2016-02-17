# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Reusable functions for stress tests """

import json
import logging
import requests
import subprocess
import time
import util.cpu
import util.netutil
import util.sysstats


def check_ds_hosts(controller_nb_interface):
    """Query number of hosts registered in ODL operational DS

    :param controller_nb_interface: namedtuple containing 1) controller_node_ip
    2)controller_restconf_port 3) controller_restconf_user
    4) controller_restconf_password
    :returns: number of hosts found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    :type controller_nb_interface: namedtuple<str,int,str,str>
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(controller_nb_interface.ip, controller_nb_interface.port))
    auth_token = (controller_nb_interface.username,
                  controller_nb_interface.password)
    try:
        datastore = requests.get(url=url,
            auth=auth_token).json()['topology'][0]
    except:
        return -1

    hosts = [node for node in datastore.get('node', []) if node['node-id'].startswith('host:')]
    return len(hosts)


def check_ds_links(controller_nb_interface):
    """Query number of links registered in ODL operational DS

    :param controller_nb_interface: namedtuple containing 1) controller_node_ip
    2)controller_restconf_port 3) controller_restconf_user
    4) controller_restconf_password
    :returns: number of hosts found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    :type controller_nb_interface: namedtuple<str,int,str,str>
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(controller_nb_interface.ip, controller_nb_interface.port))
    auth_token = (controller_nb_interface.username,
                  controller_nb_interface.password)
    try:
        datastore = requests.get(url=url,
            auth=auth_token).json()['topology'][0]
    except:
        return -1

    links = [link for link in datastore.get('link', [])]
    return len(links)

def check_ds_switches(controller_nb_interface):
    """Query number of switches registered in ODL operational DS

    :param controller_nb_interface: namedtuple containing 1) controller_node_ip
    2)controller_restconf_port 3) controller_restconf_user
    4) controller_restconf_password
    :returns: number of hosts found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    :type controller_nb_interface: namedtuple<str,int,str,str>
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(controller_nb_interface.ip, controller_nb_interface.port))
    auth_token = (controller_nb_interface.username,
                  controller_nb_interface.password)
    try:
        datastore = requests.get(url=url,
            auth=auth_token).json()['topology'][0]
    except:
        return -1

    switches = [node for node in datastore.get('node', []) if not node['node-id'].startswith('host:')]
    return len(switches)

def close_ssh_connections(ssh_clients_list):
    """Gets a list of open ssh connections (ssh_clients) and closes them.

    :param ssh_clients_list: A list of named tuples
    :type ssh_clients_list: tuple<paramiko.SSHClient>
    """

    object_id = 0
    for ssh_client in ssh_clients_list:
        if ssh_client:
            ssh_client.close()
        else:
            logging.error('[close_ssh_connections] Connection object with '
                          'id = {0} does not exist.'.format(object_id))
        object_id += 1

def command_exec_wrapper(cmd_list, prefix='', ssh_client=None,
                         data_queue=None):
    """Executes a command either locally or remotely and returns the result

    :param cmd_list: the command to be executed given in a list format of
    command and its arguments
    :param prefix: The prefix to be used for logging of executed command output
    :param ssh_client : SSH client provided by paramiko to run the command
    :param data_queue: data queue where generator output is posted line by line
    the generator process will run.
    :returns: The commands exit status
    :rtype: int
    :type cmd_list: list<str>
    :type prefix: str
    :type ssh_client: paramiko.SSHClient
    :type data_queue: multiprocessing.Queue
    """

    if ssh_client == None:
        exit_status = util.customsubprocess.check_output_streaming(cmd_list,
            prefix, data_queue)
    else:
        exit_status = util.netutil.ssh_run_command(ssh_client,
            ' '.join(cmd_list), prefix, data_queue)[0]
    return exit_status

def create_cpu_shares(controller_cpu_shares, generator_cpu_shares):
    """Returns a tuple of 2 strings, in which we have the controller and
    generator CPU shares as a comma separated values.

    :param controller_cpu_shares: Percentage of CPU resources to be used by
    controller.
    :param generator_cpu_shares: Percentage of CPU resources to be used by
    generator.
    :returns: number of cpus allocated for controller, generator
    :rtype: tuple<str,str>
    :type controller_cpu_shares: int
    :type generator_cpu_shares: int
    """

    # Define CPU affinity for controller and generator
    cpu_lists = util.cpu.compute_cpu_shares([controller_cpu_shares,
                                             generator_cpu_shares],
                                            util.sysstats.sys_nprocs())
    controller_cpus_str = ','.join(str(e) for e in cpu_lists[0])
    generator_cpus_str = ','.join(str(e) for e in cpu_lists[1])
    return (controller_cpus_str, generator_cpus_str)


def generate_json_results(results, out_json):
    """ Creates the result json file and writes test results in it

    :param results A list containing the results.
    :param out_json: The file path of json file to be created and write
    results in it
    :type results: <list<dictionary>>
    :type out_json: str
    """

    try:
        if len(results) > 0:
            with open(out_json, 'w') as ojf:
                json.dump(results, ojf)
                ojf.close()
                logging.info('[generate_json_results] Results written to {0}.'.
                             format(out_json))
        else:
            logging.error('[generate_json_results] results parameter was empty.'
                          ' Nothing to be saved')
    except:
        logging.error('[generate_json_results] output json file could not be '
                      'created. Check privileges.')


def open_ssh_connections(connections_list):
    """Gets a list of named tuples that describes the connections we want to
    initiate. Each named tuple must have the following fields:
    ['name', 'ip', 'ssh_port', 'username', 'password'] .
    It will return a tuple of paramiko.SSHClient objects.

    :param connections_list: A list of named tuples
    :returns: tuple of paramiko.SSHClient objects
    :rtype: tuple<paramiko.SSHClient>
    :type connections_list: list<collections.namedtuple>
    """

    connection_clients = []
    for connection in connections_list:
        logging.info(
            '[open_ssh_connections] Initiating SSH session with {0} node.'.
            format(connection.name))
        connection_clients.append(
            util.netutil.ssh_connect_or_return(connection, 10)
        )
    return tuple(connection_clients)


def poll_ds_thread(controller_nb_interface, boot_start_time, bootup_time_ms,
                   expected_switches, queuecomm):
    """
    Poll operational DS to discover installed switches

    :param controller_nb_interface: namedtuple containing 1) controller_node_ip
    2)controller_restconf_port 3) controller_restconf_user
    4) controller_restconf_password
    :param boot_start_time: The time we begin starting topology switches
    :param bootup_time_ms: Time to bootup switches topology (in ms). We start
    discovery process after this time.
    :param expected_switches: switches expected to find in the DS
    should discover switches (in milliseconds)
    :param queuecomm: queue for communicating with the main context
    :type controller_nb_interface: namedtuple<str,int,str,str>
    :type boot_start_time: int
    :type bootup_time_ms: int
    :type expected_switches: int
    :type queuecomm: multiprocessing.Queue
    """

    discovery_deadline = 120
    sleep_before_discovery = float(bootup_time_ms.value) / 1000

    logging.info('[poll_ds_thread] Monitor thread started')
    t_start = boot_start_time.value
    time.sleep(sleep_before_discovery)
    logging.info('[poll_ds_thread] Starting discovery')
    t_discovery_start = time.time()
    previous_discovered_switches = 0
    discovered_switches = 0

    while True:

        if (time.time() - t_discovery_start) > discovery_deadline:
            logging.info(
                '[poll_ds_thread] Deadline of {0} seconds passed, discovered '
                '{1} switches.'.format(discovery_deadline,
                                       discovered_switches))

            queuecomm.put((-1.0, discovered_switches))
            return
        else:
            discovered_switches = check_ds_switches(controller_nb_interface)
            if (discovered_switches - previous_discovered_switches) != 0:
                t_discovery_start = time.time()
                previous_discovered_switches = discovered_switches

            if discovered_switches == expected_switches:
                delta_t = time.time() - t_start
                logging.info(
                    '[poll_ds_thread] {0} switches found in {1} seconds'.
                    format(discovered_switches, delta_t))

                queuecomm.put((delta_t, discovered_switches))
                return
        time.sleep(1)


def sample_stats(cpid, ssh_client=None):
    """ Take runtime statistics

    :param cpid: controller PID
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: experiment statistics in dictionary
    :rtype: dict
    :type cpid: int
    :type ssh_client: paramiko.SSHClient
    """

    common_statistics = {}
    common_statistics['total_memory_bytes'] = \
        util.sysstats.sys_total_memory_bytes(ssh_client)
    common_statistics['controller_cwd'] = \
        util.sysstats.proc_cwd(cpid, ssh_client)
    common_statistics['controller_java_xopts'] = \
        util.sysstats.get_java_options(cpid, ssh_client)
    common_statistics['timestamp'] = \
        int(subprocess.check_output('date +%s', shell=True,
                                              universal_newlines=True).strip())
    common_statistics['date'] = subprocess.check_output('date', shell=True,
                                     universal_newlines=True).strip()
    common_statistics['used_memory_bytes'] = \
        util.sysstats.sys_used_memory_bytes(ssh_client)
    common_statistics['free_memory_bytes'] = \
        util.sysstats.sys_free_memory_bytes(ssh_client)
    common_statistics['controller_cpu_system_time'] = \
        util.sysstats.proc_cpu_system_time(cpid, ssh_client)
    common_statistics['controller_cpu_user_time'] = \
        util.sysstats.proc_cpu_user_time(cpid, ssh_client)
    common_statistics['controller_vm_size'] = \
        util.sysstats.proc_vm_size(cpid, ssh_client)
    common_statistics['controller_num_fds'] = \
        util.sysstats.proc_num_fds(cpid, ssh_client)
    common_statistics['controller_num_threads'] = \
        util.sysstats.proc_num_threads(cpid, ssh_client)
    common_statistics['one_minute_load'] = \
        util.sysstats.sys_load_average(ssh_client)[0]
    common_statistics['five_minute_load'] = \
        util.sysstats.sys_load_average(ssh_client)[1]
    common_statistics['fifteen_minute_load'] = \
        util.sysstats.sys_load_average(ssh_client)[2]

    return common_statistics


