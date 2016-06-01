# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Multinet-related utilities
"""

import common
import json
import logging
import re
import subprocess
import time
import util.customsubprocess


def multinet_pre_post_actions(action_handler):
    """
    Function that calls the multinet build and clean handlers under
    emulators/multinet folder
    :param action_handler: the full path to the multinet local handler
    :type action_handler: str
    """

    logging.debug('[{0}] Executing command: {1}'.
                  format('multinet_pre_post_actions', action_handler))
    util.customsubprocess.check_output_streaming(action_handler,
                                                 '[multinet_pre_post_actions]')

def parse_multinet_output(multinet_handler_name, multinet_output):
    """Gets the console output of a multinet handler and extracts the
    aggregated result from all workers, as a numeric value. (Helper function)
    :param multinet_handler_name: The name of multinet handler from which
    we get the results.
    :param multinet_output: The console output of multinet handler
    :returns: The aggregated result from all workers
    (aggregation function is sum)
    :rtype: int
    :type multinet_handler_name: string
    :type multinet_output: string
    :raises exception: If the result of the parsed multinet output is None
    """
    regex_result = re.search(r'INFO:root:\[{0}\]\[response data\].*'.format(multinet_handler_name), multinet_output)
    if regex_result == None:
        raise Exception('Failed to get results from {0} multinet handler.'.format(multinet_handler_name))
    else:
        result_get_flows = regex_result.group(0).replace('INFO:root:[{0}][response data] '.format(multinet_handler_name), '')
    multinet_result = sum([list(json.loads(v).values())[0] for v in json.loads(result_get_flows)])
    return multinet_result


def multinet_command_runner(exec_path, logging_prefix, multinet_base_dir,
                            is_privileged=False):
    """
    General wrapper for running multinet handlers and deploy/cleanup multinet
    scripts

    :param exec_path: the full path of handler or script to be executed
    :param logging_prefix: the logging message prefix
    :param multinet_base_dir: the full path to the multinet root folder
    :param is_privileged: flag to indicate if the executed script or handler
    will be executed in privileged mode
    :type exec_path: str
    :type logging_prefix: str
    :type is_privileged: bool
    :type multinet_base_dir: str
    """

    run_cmd_prefix = ''
    if is_privileged:
        run_cmd_prefix = 'sudo'
    multinet_run_cmd = ('{0} PYTHONPATH=\"{1}\" python {2} --json-config {3}'.
                            format(run_cmd_prefix, multinet_base_dir,
                                   exec_path,
                                   multinet_base_dir + 'config/config.json'))
    logging.debug('[{0}] multinet command to run: {1}'.
                  format(logging_prefix, multinet_run_cmd))
    return subprocess.check_output(multinet_run_cmd, stderr=subprocess.STDOUT,
                                   shell=True).decode('utf-8')


def check_topo_booted(expected_switches, group_size, group_delay_ms,
                     get_switches_handler, rest_server,
                     controller_nb_interface, multinet_base_dir, num_tries=3):
    """
    Check if a topology has been booted. Check both from the Mininet
    side and from the controller operational DS.

    :param expected_switches: expected switches that should be created by
    topology emulator
    :param group_size: group size at which switches are added in a
    Mininet topo
    :param group_delay_ms: delay between group additions
    (in milliseconds)
    :param get_switches_handler: Handler used to query the
    current number of switches in a topology from topology emulator side
    :param rest_server: named tuple containing 1) topology_node_ip
    2)rest_server_port the REST server listens to
    :param controller_nb_interface: named tuple containing 1) controller_node_ip
    2) controller_restconf_port 3) controller_restconf_user
    4) controller_restconf_password
    :param multinet_base_dir: the full path to the multinet root folder
    :param num_tries: maximum number of tries until the method identifies that
    number of discovered switches of the Mininet topology is equal to the
    number of expected Mininet switches
    :raises Exception: if we reach max number of tries and either the
    controller has not seen the topology or the topology has failed to start.
    :type expected_switches: int
    :type group_size: int
    :type group_delay_ms: int
    :type get_switches_handler: str
    :type rest_server: namedtuple<str,int>
    :type controller_nb_interface: namedtuple<str,int,str,str>
    :type multinet_base_dir: str
    :type num_tries: int
    """

    mininet_group_delay = float(group_delay_ms)/1000
    discovered_switches = 0
    ds_switches = 0
    tries = 0

    while tries < num_tries:
        logging.info('[check_topo_booted] Check if topology is up.')

        # Here we sleep in order to give time to the controller to discover
        # topology through the LLDP protocol.
        time.sleep(int(expected_switches/group_size) * \
                   mininet_group_delay + 15)
        try:
            result_get_sw = multinet_command_runner(get_switches_handler,
                '[get_switches_handler]', multinet_base_dir,
                is_privileged=False)
            # get Multinet switches number
            discovered_switches = \
                parse_multinet_output('get_switches_topology_handler',
                                      result_get_sw)
            logging.info('[check_topo_booted] Discovered {0} switches'
                          ' at the Multinet side'.format(discovered_switches))
            # get controller switches number from DS
            ds_switches = common.check_ds_switches(controller_nb_interface)
            logging.info('[check_topo_booted] Discovered {0} switches'
                          ' at the controller side'.format(ds_switches))
            # check if the controller has discovered Multinet topology
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


def generate_multinet_config(controller_sb_interface, multinet_rest_server,
                             multinet_node, multinet_size, multinet_group_size,
                             multinet_group_delay_ms, multinet_hosts_per_switch,
                             multinet_topology_type, multinet_switch_type,
                             multinet_worker_ip_list, multinet_worker_port_list,
                             multinet_base_dir, traffic_generation_duration_ms,
                             interpacket_delay_ms):
    """
    Generates a new json configuration file for multinet, according to the
    configuration values that are passed as parameters.
    :param controller_sb_interface: named_tuple containing controller
    SouthBound parameters 1)ip address of the controller 2) port number of
    SouthBound interface
    :param multinet_rest_server: named_tuple containing multinet master rest
    server parameters 1)ip address of the master 2) port number of
    master rest server
    :param multinet_node:Named tuple containing information to establish ssh
    connection with multinet master node with the following parameters 1)name
    2)ip address of multinet  master node 3)ssh port of multinet master node
    4)user name to make ssh login in multinet master node 5)password to make
    ssh login in multinet master node
    :param multinet_size: number of switches of the topology
    :param multinet_group_size: the number of switches to be booted in one
    batch
    :param multinet_group_delay_ms: the delay in milliseconds between each
    group boot
    :param multinet_hosts_per_switch: number of hosts to connect on each
    switch of the topology
    :param multinet_topology_type: the type of the topology we want to create
    :param multinet_switch_type: the type of openflow switch we want to create
    :param multinet_worker_ip_list: a list of ip addresses of multinet workers
    :param multinet_worker_port_list: a list of port numbers of multinet workers
    :param multinet_base_dir: the full path to the multinet root folder
    :param traffic_generation_duration_ms:
    :param interpacket_delay_ms:
    :type controller_sb_interface: collection.namedtuple(<str>, <int>)
    :type multinet_rest_server: collection.namedtuple(<str>, <int>)
    :type multinet_node: collection.namedtuple(<str>, <str>, <int>, <str>, <str>)
    :type multinet_size: int
    :type multinet_group_size: int
    :type multinet_group_delay_ms: int
    :type multinet_hosts_per_switch: int
    :type multinet_topology_type: str
    :type multinet_switch_type: str
    :type multinet_worker_ip_list: list<str>
    :type multinet_worker_port_list: list<int>
    :type multinet_base_dir:<str>
    :type traffic_generation_duration_ms: int
    :type interpacket_delay_ms: int
    """

    multinet_config_path = '{0}/config/config.json'.format(multinet_base_dir)
    with open(multinet_config_path, 'r') as config_json_file:
        config_json = json.load(config_json_file)

    config_json['master_ip'] = multinet_rest_server.ip
    config_json['master_port'] = multinet_rest_server.port
    config_json['worker_ip_list'] = multinet_worker_ip_list
    config_json['worker_port_list'] = multinet_worker_port_list
    config_json['deploy']['multinet_base_dir'] = multinet_base_dir
    config_json['deploy']['ssh_port'] = multinet_node.ssh_port
    config_json['deploy']['username'] = multinet_node.username
    config_json['deploy']['password'] = multinet_node.password
    config_json['topo']['controller_ip_address'] = controller_sb_interface.ip
    config_json['topo']['controller_of_port'] = controller_sb_interface.port
    config_json['topo']['switch_type'] = multinet_switch_type
    config_json['topo']['topo_type'] = multinet_topology_type
    config_json['topo']['topo_size'] = multinet_size
    config_json['topo']['group_size'] = multinet_group_size
    config_json['topo']['group_delay'] = multinet_group_delay_ms
    config_json['topo']['hosts_per_switch'] = multinet_hosts_per_switch
    config_json['topo']['traffic_generation_duration_ms'] = \
        traffic_generation_duration_ms
    config_json['topo']['interpacket_delay_ms'] = interpacket_delay_ms

    with open(multinet_config_path, 'w') as config_json_file:
        json.dump(config_json, config_json_file)


def get_topology_flows(multinet_base_dir, get_flows_handler):
    result_get_flows = multinet_utils.multinet_command_runner(get_flows_handler,
        '[get_flows_handler]', multinet_base_dir,
        is_privileged=False)
    # Get total flows from multinet topology switches
    discovered_flows = parse_multinet_output('get_flows_topology_handler', result_get_flows)
    return discovered_flows