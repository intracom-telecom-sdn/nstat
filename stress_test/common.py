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
import util.file_ops
import util.netutil
import util.process
import util.sysstats


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
        exit_status, cmd_output = util.netutil.ssh_run_command(ssh_client,
            ' '.join(cmd_list), prefix, data_queue)
    return exit_status


def check_ds_switches(controller_ip, controller_restconf_port, auth_token):
    """Query number of switches registered in ODL operational DS

    :param controller_ip: controller IP address
    :param controller_restconf_port: controller restconf port
    :param auth_token: tuple with controller restconf user and password
    (controller_restconf_user, controller_restconf_password)
    :returns: number of switches found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    :type controller_ip: str
    :type controller_restconf_port: int
    :type auth_token: tuple<str>
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(controller_ip, controller_restconf_port))

    try:
        datastore = requests.get(url=url,
            auth=auth_token).json()['topology'][0]
    except:
        return -1

    switches = [node for node in datastore.get('node', []) if not node['node-id'].startswith('host:')]
    return len(switches)


def check_ds_hosts(controller_ip, controller_restconf_port, auth_token):
    """Query number of hosts registered in ODL operational DS

    :param controller_ip: controller IP address
    :param controller_restconf_port: controller restconf port
    :param auth_token: tuple with controller restconf user and password
    (controller_restconf_user, controller_restconf_password)
    :returns: number of hosts found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    :type controller_ip: str
    :type controller_restconf_port: int
    :type auth_token: tuple<str>
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(controller_ip, controller_restconf_port))

    try:
        datastore = requests.get(url=url,
            auth=auth_token).json()['topology'][0]
    except:
        return -1

    hosts = [node for node in datastore.get('node', []) if node['node-id'].startswith('host:')]
    return len(hosts)


def check_ds_links(controller_ip, controller_restconf_port, auth_token):
    """Query number of links registered in ODL operational DS

    :param controller_ip: controller IP address
    :param controller_restconf_port: controller restconf port
    :param auth_token: tuple with controller restconf user and password
    (controller_restconf_user, controller_restconf_password)
    :returns: number of links found, 0 if none exists and -1 in case of error.
    :rtype: int
    :type controller_ip: str
    :type controller_restconf_port: int
    :type auth_token: tuple<str>
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(controller_ip, controller_restconf_port))

    try:
        datastore = requests.get(url=url,
            auth=auth_token).json()['topology'][0]
    except:
        return -1

    links = [link for link in datastore.get('link', [])]
    return len(links)


def poll_ds_thread(controller_ip, controller_restconf_port,
                   controller_restconf_user, controller_restconf_password,
                   boot_start_time, bootup_time_ms, expected_switches,
                   discovery_deadline_ms, queuecomm):
    """
    Poll operational DS to discover installed switches

    :param controller_ip: controller IP address
    :param controller_restconf_port: controller restconf port
    :param auth_token: tuple with controller restconf user and controller
    restconf password (controller_restconf_user, controller_restconf_password)
    :param boot_start_time: The time we begin starting topology switches
    :param bootup_time_ms: Time to bootup switches topology (in ms). We start
    discovery process after this time.
    :param expected_switches: switches expected to find in the DS
    :param discovery_deadline_ms: deadline (in ms) at which the thread
    should discover switches (in milliseconds)
    :param queuecomm: queue for communicating with the main context
    :type controller_ip: str
    :type controller_restconf_port: int
    :type controller_restconf_auth_token: tuple<str>
    :type boot_start_time: int
    :type bootup_time_ms: int
    :type expected_switches: int
    :type discovery_deadline_ms: float
    :type queuecomm: multiprocessing.Queue
    """

    discovery_deadline = float(discovery_deadline_ms.value) / 1000
    sleep_before_discovery = float(bootup_time_ms.value) / 1000

    logging.info('[poll_ds_thread] Monitor thread started')
    t_start = boot_start_time.value
    time.sleep(sleep_before_discovery)
    logging.info('[poll_ds_thread] Starting discovery')
    t_discovery_start = time.time()
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
            discovered_switches = check_ds_switches(controller_ip.value.decode(),
                controller_restconf_port.value,
                (controller_restconf_user.value.decode(),
                 controller_restconf_password.value.decode()))

            if discovered_switches == expected_switches.value:
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
    :returns: the statistics in a dictionary
    :rtype: dict
    :type cpid: int
    :type ssh_client: paramiko.SSHClient
    """

    common_statistics = {}
    common_statistics['total_memory_bytes'] = \
        util.sysstats.sys_total_memory_bytes(ssh_client)
    common_statistics['controller_cwd'] = util.sysstats.proc_cwd(cpid, ssh_client)
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
    common_statistics['one_minute_load'] = util.sysstats.sys_load_average(ssh_client)[0]
    common_statistics['five_minute_load'] = util.sysstats.sys_load_average(ssh_client)[1]
    common_statistics['fifteen_minute_load'] = \
        util.sysstats.sys_load_average(ssh_client)[2]
    return common_statistics


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
                logging.info('[generate_json_results] Results writen to {0}.'.
                             format(out_json))
        else:
            logging.error('[generate_json_results] results parameter was empty.'
                          ' Nothing to be saved')
    except:
        logging.error('[generate_json_results] output json file could not be '
                      'created. Check privileges.')


def controller_pre_actions(controller_handlers_set, controller_rebuild,
                           controller_ssh_client, java_opts, controller_port):
    """ Performs all necessary actions before starting a test. Pre actions
    are 1) rebuild_controller 2) check_for_active_controller
    3) generate_controller_xml_files

    :param controller_handlers_set: tuple containing
    :param controller_rebuild: if SET controller rebuild is performed
    :param controller_ssh_client: paramiko.SSHClient object
    :param java_opts: controller JAVA options
    :param controller_port: controller port to check
    :type controller_handlers_set: collections.namedtuple<str>
    :type controller_rebuild: boolean
    :type controller_ssh_client: paramiko.SSHClient
    :type java_opts: str
    :type controller_port: int
    """
    try:
        if controller_rebuild:
            logging.info('[controller_pre_actions] building controller')
            controller_utils.rebuild_controller(
                controller_handlers_set.ctrl_build_handler,
                controller_ssh_client)

        logging.info('[controller_pre_actions] checking for other active '
                     'controllers')
        controller_utils.check_for_active_controller(controller_port,
            controller_ssh_client)
        logging.info('[controller_pre_actions] starting and stopping controller'
                     ' to generate xml files')
        controller_utils.generate_controller_xml_files(
            controller_handlers_set.ctrl_start_handler,
            controller_handlers_set.controller_stop_handler,
            controller_handlers_set.controller_status_handler,
            controller_port,' '.join(java_opts), controller_ssh_client)
    except:
        logging.error('[controller_pre_actions] controller pre actions could '
                      'not be finalized.')