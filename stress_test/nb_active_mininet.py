# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NorthBound Performance test """

import collections
import common
import controller_utils
import itertools
import json
import logging
import mininet_utils
import multiprocessing
import os
import report_spec
import sys
import time
import util.customsubprocess
import util.file_ops
import util.netutil


#import emulators.nb_generator.nb_gen

def mininet_topo_check_booted(expected_switches, mininet_group_size,
                              mininet_group_delay_ms,
                              mininet_get_switches_handler, mininet_ip,
                              mininet_rest_server_port, ctrl_ip,
                              ctrl_port, controller_restconf_user,
                              controller_restconf_password, num_tries=3):
    """
    Check if a Mininet topology has been booted. Check both from the Mininet
    side and from the controller operational DS.

    :param expected_switches: expected Mininet switches
    :param mininet_group_size: group size at which switches where added in a
    Mininet topo
    :param mininet_group_delay_ms: delay between group additions
    (in milliseconds)
    :param mininet_get_switches_handler: Mininet handler used to query the
    current number of switches in a Mininet topology
    :param mininet_ip: Mininet node IP
    :param mininet_rest_server_port: port of the Mininet node REST server
    :param ctrl_ip: controller IP
    :param ctrl_port: controller RESTconf port
    :param controller_restconf_user: RESTconf username
    :param controller_restconf_password: RESTconf password
    :param num_tries: maximum number of tries until the method identifies that
    number of discovered switches of the Mininet topology is equal to the
    number of expected Mininet switches
    :raises Exception: If we reach max number of tries and either the
    controller has not seen the topology or the topology has failed to start.
    :type expected_switches: int
    :type mininet_group_size: int
    :type mininet_group_delay_ms: int
    :type mininet_get_switches_handler: str
    :type mininet_ip: str
    :type mininet_rest_server_port: int
    :type ctrl_ip: str
    :type ctrl_port: int
    :type controller_restconf_user: str
    :type controller_restconf_password: str
    :type num_tries: int
    """

    mininet_group_delay = float(mininet_group_delay_ms)/1000
    discovered_switches = 0
    ds_switches = 0
    tries = 0
    auth_token = (controller_restconf_user, controller_restconf_password)

    while tries < num_tries:
        logging.info('[mininet_topo_check_booted] Check if topology is up.')

        # Here we sleep in order to give time to the controller to discover
        # topology through the LLDP protocol.
        time.sleep(int(expected_switches/mininet_group_size) * \
                   mininet_group_delay + 15)
        outq = multiprocessing.Queue()

        try:
            util.customsubprocess.check_output_streaming(
                [mininet_get_switches_handler, mininet_ip,
                 str(mininet_rest_server_port)],
                '[mininet_get_switches_handler]', queue=outq)
            discovered_switches = int(outq.get().strip())
            logging.info('[mininet_topo_check_booted] Discovered {0} switches'
                          ' at the Mininet side'.format(discovered_switches))

            ds_switches = common.check_ds_switches(ctrl_ip, ctrl_port,
                                                   auth_token)
            logging.info('[mininet_topo_check_booted] Discovered {0} switches'
                          ' at the controller side'.format(ds_switches))
            if discovered_switches == expected_switches and \
                ds_switches == expected_switches and expected_switches != 0:
                return

        except:
            pass

        tries += 1

    raise Exception('Topology did not fully initialized. Expected {0} '
                    'switches, but found {1} at the Mininet side and {2} '
                    'at the controller side.'.
                    format(expected_switches, discovered_switches,
                           ds_switches))


def nb_active_mininet_run(out_json, ctrl_base_dir, nb_generator_base_dir,
                          mininet_base_dir, conf, output_dir, log_level):
    """Run NB active test with Mininet.

    :param out_json: the JSON output file
    :param ctrl_base_dir: controller base directory
    :param mininet_base_dir: Mininet base directory
    :param conf: JSON configuration dictionary
    :param output_dir: directory to store output files
    :param log_level: This parameter is used in order to pass NSTAT
    --logging-level argument to NorthBound generator.
    :type out_json: str
    :type ctrl_base_dir: str
    :type mininet_base_dir: str
    :type conf: dict
    :type output_dir: str
    :type log_level: str
    """



    test_type = '[nb_active_mininet]'
    logging.info('{0} initializing test parameters.'.format(test_type))

    # Global variables read-write shared between monitor and main thread
    global_sample_id = 0
    cpid = 0

    # Mininet parameters
    mininet_rest_server_boot = mininet_base_dir + \
        conf['mininet_rest_server_boot']
    mininet_stop_switches_handler = mininet_base_dir + \
        conf['mininet_stop_switches_handler']
    mininet_get_switches_handler = mininet_base_dir + \
        conf['mininet_get_switches_handler']
    mininet_init_topo_handler = mininet_base_dir + \
        conf['mininet_init_topo_handler']
    mininet_start_topo_handler = mininet_base_dir + \
        conf['mininet_start_topo_handler']

    mininet_rest_server_port = conf['mininet_rest_server_port']

    # Northbound generator node parameters
    nb_generator_run_handler = nb_generator_base_dir + \
        conf['nb_generator_run_handler']
    nb_generator_host_ip = conf['nb_generator_host_ip']


    # Controller parameters
    controller_build_handler = ctrl_base_dir + conf['controller_build_handler']
    controller_start_handler = ctrl_base_dir + conf['controller_start_handler']
    controller_status_handler = \
        ctrl_base_dir + conf['controller_status_handler']
    controller_stop_handler = ctrl_base_dir + conf['controller_stop_handler']
    controller_clean_handler = ctrl_base_dir + conf['controller_clean_handler']
    controller_statistics_handler = \
        ctrl_base_dir + conf['controller_statistics_handler']
    controller_logs_dir = ctrl_base_dir + conf['controller_logs_dir']
    controller_rebuild = conf['controller_rebuild']
    controller_cleanup = conf['controller_cleanup']
    controller_restart = conf['controller_restart']
    controller_port = conf['controller_port']
    controller_restconf_port = conf['controller_restconf_port']
    controller_restconf_user = conf['controller_restconf_user']
    controller_restconf_password = conf['controller_restconf_password']

    # Various test parameters
    flow_delete_flag = conf['flow_delete_flag']
    node_parameters = collections.namedtuple('ssh_connection',
        ['name', 'ip', 'ssh_port', 'username', 'password'])
    controller_handlers = collections.namedtuple('controller_handlers',
        ['ctrl_build_handler','ctrl_start_handler','ctrl_status_handler',
         'ctrl_stop_handler', 'ctrl_clean_handler'])
    controller_handlers_set = controller_handlers(controller_build_handler,
        controller_start_handler, controller_status_handler,
        controller_stop_handler, controller_clean_handler)
    controller_node = node_parameters('Controller',
                                      conf['controller_node_ip'],
                                      int(conf['controller_node_ssh_port']),
                                      conf['controller_node_username'],
                                      conf['controller_node_password'])
    mininet_node = node_parameters('Mininet', conf['mininet_node_ip'],
                                   int(conf['mininet_node_ssh_port']),
                                   conf['mininet_node_username'],
                                   conf['mininet_node_password'])
    nb_generator_node = node_parameters('Generator',
                                        conf['nb_generator_node_ip'],
                                        int(conf['nb_generator_node_ssh_port']),
                                        conf['nb_generator_node_username'],
                                        conf['nb_generator_node_password'])
    # list of samples: each sample is a dictionary that contains
    # all information that describes a single measurement, i.e.:
    #    - the actual performance results
    #    - secondary runtime statistics
    #    - current values of test dimensions (dynamic)
    #    - test configuration options (static)
    total_samples = []
    java_opts = conf['java_opts']

    try:
        # Before proceeding with the experiments check validity of all
        # handlers
        util.file_ops.check_filelist([controller_build_handler, controller_start_handler,
        controller_status_handler, controller_stop_handler,
        controller_clean_handler, controller_statistics_handler,
        mininet_rest_server_boot, mininet_stop_switches_handler,
        mininet_get_switches_handler, mininet_start_topo_handler,
        mininet_init_topo_handler])

        # Opening connection with mininet_node_ip and returning
        # cbench_ssh_client to be utilized in the sequel
        mininet_ssh_client, controller_ssh_client, nb_generator_ssh_client = \
            common.open_ssh_connections([mininet_node,
                controller_node, nb_generator_node])

        # Controller common actions: rebuild controller if controller_rebuild is
        # SET, check_for_active controller, generate_controller_xml_files
        controller_utils.controller_pre_actions(controller_handlers_set,
                                      controller_rebuild, controller_ssh_client,
                                      java_opts, controller_port)

        # Run tests for all possible dimensions
        for (total_flows,
             flow_operations_delay_ms,
             mininet_size,
             flow_workers,
             mininet_group_size,
             mininet_group_delay_ms,
             mininet_hosts_per_switch,
             mininet_topology_type,
             controller_statistics_period_ms) in \
             itertools.product(conf['total_flows'],
                               conf['flow_operations_delay_ms'],
                               conf['mininet_size'],
                               conf['flow_workers'],
                               conf['mininet_group_size'],
                               conf['mininet_group_delay_ms'],
                               conf['mininet_hosts_per_switch'],
                               conf['mininet_topology_type'],
                               conf['controller_statistics_period_ms']):

            logging.info('{0} changing controller statistics period to {1} ms'.
                format(test_type, controller_statistics_period_ms))
            controller_utils.controller_changestatsperiod(
                controller_statistics_handler, controller_statistics_period_ms,
                controller_ssh_client)

            logging.info('{0} booting up Mininet REST server'.
                          format(test_type))
            mininet_utils.start_mininet_server(mininet_ssh_client,
                mininet_rest_server_boot, mininet_node.ip,
                mininet_rest_server_port)

            logging.info('{0} starting controller'.format(test_type))
            cpid = controller_utils.start_controller(
                controller_start_handler, controller_status_handler,
                controller_port, ' '.join(conf['java_opts']),
                controller_ssh_client)

            logging.info('{0} OK, controller status is 1.'.format(test_type))

            logging.info(
                '{0} initializing topology on REST server.'.format(test_type))
            mininet_utils.init_mininet_topo(mininet_init_topo_handler,
                mininet_node.ip, mininet_rest_server_port, controller_node.ip,
                controller_port, mininet_topology_type, mininet_size,
                mininet_group_size, mininet_group_delay_ms,
                mininet_hosts_per_switch)

            logging.info('{0} starting Mininet topology.'.format(test_type))
            mininet_utils.start_mininet_topo(mininet_start_topo_handler,
                mininet_node.ip, mininet_rest_server_port)

            mininet_topo_check_booted(mininet_size, mininet_group_size,
                                      mininet_group_delay_ms,
                                      mininet_get_switches_handler,
                                      mininet_node.ip,
                                      mininet_rest_server_port,
                                      controller_node.ip,
                                      controller_restconf_port,
                                      controller_restconf_user,
                                      controller_restconf_password)

            flow_discovery_deadline_ms = 240000

            cmd = ('cd {0}; python3.4 {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}'.
                format(nb_generator_base_dir, nb_generator_run_handler,
                       controller_node.ip, controller_restconf_port,
                       total_flows, flow_workers,
                       flow_operations_delay_ms, flow_delete_flag,
                       flow_discovery_deadline_ms, controller_restconf_user,
                       controller_restconf_password, log_level))
            logging.debug('{0} Generator handler command:{1}.'.
                          format(test_type, cmd))

            exit_status , output = util.netutil.ssh_run_command(
                nb_generator_ssh_client, cmd , '[generator_run_handler]')

            if exit_status!=0:
                raise Exception('{0} northbound generator failed'.
                                format(test_type))

            results = json.loads(output)

            # Getting results
            statistics = common.sample_stats(cpid, controller_ssh_client)
            statistics['global_sample_id'] = global_sample_id
            global_sample_id += 1
            statistics['controller_node_ip'] = controller_node.ip
            statistics['controller_port'] = str(controller_port)
            statistics['controller_restart'] = controller_restart
            statistics['total_flows'] = total_flows
            statistics['mininet_size'] = mininet_size
            statistics['mininet_topology_type'] = mininet_topology_type
            statistics['mininet_hosts_per_switch'] = \
                mininet_hosts_per_switch
            statistics['mininet_group_size'] = mininet_group_size
            statistics['mininet_group_delay_ms'] = mininet_group_delay_ms
            statistics['controller_statistics_period_ms'] = \
                controller_statistics_period_ms
            statistics['flow_operation_delay_ms'] = flow_operations_delay_ms
            statistics['flow_workers'] = flow_workers
            statistics['add_flows_transmission_time'] = results[0]
            statistics['add_flows_time'] = results[1]
            if flow_delete_flag:
                statistics['delete_flows_transmission_time'] = results[-3]
                statistics['delete_flows_time'] = results[-2]
            statistics['failed_flow_operations'] = results[-1]
            statistics['flow_delete_flag'] = str(flow_delete_flag)
            total_samples.append(statistics)

            logging.debug('{0} stopping Mininet topology.'.format(test_type))


            mininet_utils.stop_mininet_topo(mininet_stop_switches_handler,
                mininet_node.ip, mininet_rest_server_port)

            logging.debug('{0} stopping controller.'.format(test_type))
            controller_utils.stop_controller(controller_stop_handler,
                controller_status_handler, cpid, controller_ssh_client)

            logging.debug('{0} killing REST daemon in Mininet VM.'.
                          format(test_type))
            mininet_utils.stop_mininet_server(mininet_ssh_client,
                                              mininet_rest_server_port)

    except:
        logging.error('{0} :::::::::: Exception :::::::::::'.format(test_type))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error('{0} Exception: {1}, {2}.'.
                      format(test_type, exc_type, exc_tb.tb_lineno))
        logging.exception('')

        errors = str(exc_obj).rstrip().split('\n')
        for error in errors:
            logging.error('{0} {1}'.format(test_type, error))

    finally:
        logging.info('{0} finalizing test.'.format(test_type))

        logging.info('{0} creating test output directory if not present.'.
                     format(test_type))
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        logging.info('{0} saving results to JSON file.'.format(test_type))
        common.generate_json_results(total_samples, out_json)

        try:
            logging.info('{0} stopping controller.'.format(test_type))
            controller_utils.stop_controller(controller_stop_handler,
                controller_status_handler, cpid, controller_ssh_client)
        except:
            pass

        try:
            logging.info('{0} collecting logs'.format(test_type))
            util.netutil.copy_remote_directory(controller_node,
                controller_logs_dir, output_dir+'/log')
        except:
            logging.error('{0} {1}'.format(
                test_type, 'failed transferring controller logs dir.'))

        if controller_cleanup:
            logging.info('{0} cleaning controller directory'.format(test_type))
            controller_utils.cleanup_controller(controller_clean_handler,
                                                controller_ssh_client)


        try:
            logging.info('{0} stopping REST daemon in Mininet node.'.
                          format(test_type))
            mininet_utils.stop_mininet_server(mininet_ssh_client,
                                              mininet_rest_server_port)
        except:
            pass

        # Closing ssh connections with controller/Mininet nodes
        if controller_ssh_client:
            controller_ssh_client.close()
        else:
            logging.error('{0} controller ssh connection does not exist.'.
                          format(test_type))
        if mininet_ssh_client:
            mininet_ssh_client.close()
        else:
            logging.error('{0} Mininet ssh connection does not exist.'.
                          format(test_type))
        if nb_generator_ssh_client:
            nb_generator_ssh_client.close()
        else:
            logging.error('{0} NB generator node ssh connection does not exist.'.
                          format(test_type))

def get_report_spec(test_type, config_json, results_json):
    """
    Return the report specification for this test

    :param test_type: test short description (title)
    :param config_json: JSON config path
    :param results_json: JSON results path
    :returns: report specification for this test
    :rtype: ReportSpec
    :type: test_type: str
    :type: config_json: str
    :type: results_json: str
    """

    report_spec_obj = report_spec.ReportSpec(
        config_json, results_json, '{0}'.format(test_type),
        [report_spec.TableSpec(
            '1d', 'Test configuration parameters (detailed)',
            [('controller_name', 'Controller name'),
             ('controller_build_handler', 'Controller build script'),
             ('controller_start_handler', 'Controller start script'),
             ('controller_stop_handler', 'Controller stop script'),
             ('controller_status_handler', 'Controller status script'),
             ('controller_clean_handler', 'Controller cleanup script'),
             ('controller_statistics_handler', 'Controller statistics script'),
             ('controller_node_ip', 'Controller IP node address'),
             ('controller_port', 'Controller listening port'),
             ('controller_rebuild', 'Controller rebuild between test repeats'),
             ('controller_logs_dir', 'Controller log save directory'),
             ('controller_restconf_port', 'Controller RESTconf port'),
             ('mininet_rest_server_boot', 'Mininet boot handler'),
             ('mininet_stop_switches_handler',
              'Mininet stop switches handler'),
             ('mininet_get_switches_handler', 'Mininet get switches handler'),
             ('mininet_init_topo_handler',
              'Mininet initialize topology handler'),
             ('mininet_start_topo_handler', 'Mininet start topology handler'),
             ('mininet_node_ip', 'Mininet node IP'),
             ('mininet_rest_server_port', 'Mininet node REST server port'),
             ('mininet_size', 'Mininet network size'),
             ('mininet_topology_type', 'Mininet topology type'),
             ('mininet_hosts_per_switch', 'Mininet hosts per switch'),
             ('flow_workers', 'Flow worker threads'),
             ('total_flows', 'Total flows to be added'),
             ('flow_operations_delay_ms', 'Delay between flow operations'),
             ('flow_delete_flag', 'Flow delete flag'),
             ('java_opts', 'JVM options')], config_json)],
        [report_spec.TableSpec('2d', 'Test results',
            [('global_sample_id', 'Sample ID'),
             ('timestamp', 'Sample timestamp (seconds)'),
             ('date', 'Sample timestamp (date)'),
             ('total_flows', 'Total flow operations'),
             ('failed_flow_operations', 'Total failed flow operations'),
             ('add_flows_transmission_time',
              'Total time of NB Restconf calls for flows addition (seconds)'),
             ('add_flows_time', 'Add flows time (seconds)'),
             ('delete_flows_transmission_time',
              'Total time of NB Restconf calls for flows deletion (seconds)'),
             ('delete_flows_time', 'Delete flows time (seconds)'),
             ('flow_operation_delay_ms', 'Flow operation delay (milliseconds)'),
             ('flow_workers', 'Flow workers'),
             ('flow_delete_flag', 'Deletion flag'),
             ('mininet_size', 'Mininet Size'),
             ('mininet_topology_type', 'Mininet Topology Type'),
             ('mininet_hosts_per_switch', 'Mininet Hosts per Switch'),
             ('mininet_group_size', 'Mininet Group Size'),
             ('mininet_group_delay_ms', 'Mininet Group Delay (ms)'),
             ('controller_node_ip', 'Controller IP node address'),
             ('controller_port', 'Controller port'),
             ('controller_vm_size', 'Controller VM size'),
             ('controller_java_xopts', 'Java options'),
             ('free_memory_bytes', 'System free memory in bytes'),
             ('used_memory_bytes', 'System used memory in bytes'),
             ('total_memory_bytes', 'System total memory in bytes'),
             ('one_minute_load', 'One minute load'),
             ('five_minute_load', 'Five minutes load'),
             ('fifteen_minute_load', 'Fifteen minutes load'),
             ('controller_cpu_system_time', 'Controller CPU system time'),
             ('controller_cpu_user_time', 'Controller CPU user time'),
             ('controller_num_threads', 'Controller num of threads'),
             ('controller_num_fds', 'Controller num of fds'),
             ('controller_statistics_period_ms',
              'Controller statistics period (ms)')], results_json)])

    return report_spec_obj
