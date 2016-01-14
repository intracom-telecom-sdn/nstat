# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Multinet-related utilities
"""

import json
import logging
import util.customsubprocess


def multinet_pre_post_actions(multinet_base_dir, action):
    """
    Function that calls the multinet build and clean handlers under
    emulators/multinet folder
    :param multinet_base_dir: the full path to the multinet root folder
    :param action: the type of pre or post action to execute. Can be either
    build or clean
    :type multinet_base_dir: str
    :type action: str
    :raises ValueError: if invalid action is given as input
    """

    exec_cmd = '{0}{1}.sh'.format(multinet_base_dir, action)
    print(exec_cmd)
    if action != 'build' and action != 'clean':
        logging.error('[{0}] Action {1} is not valid'.
                      format('multinet_pre_post_actions', action))
        raise ValueError('Invalid action value.')
    util.customsubprocess(exec_cmd, '[{0}] Running multinet {1} action'.
                              format('multinet_pre_post_actions', action))


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
    multinet_run_cmd = ('{0} PYTHONPATH={1} python {2} --json-config {3}'.
                            format(run_cmd_prefix, multinet_base_dir,
                                   exec_path,
                                   multinet_base_dir + '/config/config.json'))
    logging.debug('[{0}] multinet command to run: {1}'.
                  format(logging_prefix, multinet_run_cmd))
    util.customsubprocess.check_output_streaming(multinet_run_cmd,
                                                 '[{0}]'.format(logging_prefix))


def generate_multinet_config(controller_sb_interface, multinet_rest_server,
                             multinet_node, multinet_size, multinet_group_size,
                             multinet_group_delay_ms, multinet_hosts_per_switch,
                             multinet_topology_type, multinet_switch_type,
                             multinet_worker_ip_list, multinet_worker_port_list,
                             multinet_base_dir):
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

    with open(multinet_config_path, 'w') as config_json_file:
        json.dump(config_json, config_json_file)

