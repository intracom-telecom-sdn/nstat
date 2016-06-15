# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NorthBound Performance test """

import common
import conf_collections_util
import controller_utils
import itertools
import json
import logging
import multinet_utils
import nb_utils
import os
import report_spec
import sys
import time
import util.file_ops
import util.netutil


def nb_active_scalability_multinet_run(out_json, ctrl_base_dir,
                                       nb_generator_base_dir, multinet_base_dir,
                                       conf, output_dir, log_level):

    """Run northbound active test with Multinet.

    :param out_json: the JSON output file
    :param ctrl_base_dir: controller base directory
    :param nb_generator_base_dir: northbound generator base directory
    :param multinet_base_dir: Multinet base directory
    :param conf: JSON configuration dictionary
    :param output_dir: directory to store output files
    :param log_level: This parameter is used in order to pass NSTAT
    --logging-level argument to NorthBound generator.
    :type out_json: str
    :type ctrl_base_dir: str
    :type nb_generator_base_dir: str
    :type multinet_base_dir: str
    :type conf: dict
    :type output_dir: str
    :type log_level: str
    """

    test_type = '[nb_active_scalability_multinet]'
    logging.info('{0} initializing test parameters.'.format(test_type))

    # Global variables read-write shared between monitor and main thread
    global_sample_id = 0
    cpid = 0
    flow_delete_flag = conf['flow_delete_flag']
    flows_per_request = conf['flows_per_request']

    # Multinet parameters
    multinet_hosts_per_switch = conf['topology_hosts_per_switch']
    multinet_worker_topo_size = conf['topology_size']
    multinet_worker_ip_list = conf['multinet_worker_ip_list']
    multinet_worker_port_list = conf['multinet_worker_port_list']
    multinet_workers = len(multinet_worker_ip_list)

    # Northbound generator node parameters
    if 'nb_generator_cpu_shares' in conf:
        nb_generator_cpu_shares = conf['nb_generator_cpu_shares']

    multinet_switch_type = conf['multinet_switch_type']

    # Controller parameters
    controller_logs_dir = ctrl_base_dir + conf['controller_logs_dir']
    controller_rebuild = conf['controller_rebuild']
    controller_cleanup = conf['controller_cleanup']
    controller_restart = conf['controller_restart']
    if 'controller_cpu_shares' in conf:
        controller_cpu_shares = conf['controller_cpu_shares']
    else:
        controller_cpu_shares = 100

    # set named tuples
    controller_handlers_set = conf_collections_util.controller_handlers(
        ctrl_base_dir + conf['controller_build_handler'],
        ctrl_base_dir + conf['controller_start_handler'],
        ctrl_base_dir + conf['controller_status_handler'],
        ctrl_base_dir + conf['controller_stop_handler'],
        ctrl_base_dir + conf['controller_clean_handler'],
        ctrl_base_dir + conf['controller_statistics_handler'],
        '',
        ctrl_base_dir + conf['controller_persistent_handler']
        )
    multinet_handlers_set = conf_collections_util.topology_generator_handlers(
        multinet_base_dir + conf['topology_rest_server_boot'],
        multinet_base_dir + conf['topology_stop_switches_handler'],
        multinet_base_dir + conf['topology_get_switches_handler'],
        multinet_base_dir + conf['topology_init_handler'],
        multinet_base_dir + conf['topology_start_switches_handler'],
        multinet_base_dir + conf['topology_rest_server_stop'],
        '',
        multinet_base_dir + conf['topology_get_flows_handler']
        )
    multinet_local_handlers_set = \
        conf_collections_util.multinet_local_handlers(
        multinet_base_dir + conf['multinet_build_handler'],
        multinet_base_dir + conf['multinet_clean_handler'])

    nb_generator_handlers_set = conf_collections_util.nb_generator_handlers(
        nb_generator_base_dir + conf['nb_generator_run_handler'])
    controller_node = conf_collections_util.node_parameters('Controller',
        conf['controller_node_ip'], int(conf['controller_node_ssh_port']),
        conf['controller_node_username'], conf['controller_node_password'])
    multinet_node = conf_collections_util.node_parameters('Multinet',
        conf['topology_node_ip'], int(conf['topology_node_ssh_port']),
        conf['topology_node_username'], conf['topology_node_password'])
    controller_sb_interface = conf_collections_util.controller_southbound(
        conf['controller_node_ip'], conf['controller_port'])
    controller_nb_interface = conf_collections_util.controller_northbound(
        conf['controller_node_ip'], conf['controller_restconf_port'],
        conf['controller_restconf_user'], conf['controller_restconf_password'])
    multinet_rest_server = conf_collections_util.multinet_server(
        conf['topology_node_ip'], conf['topology_rest_server_port'])
    nb_generator_node = conf_collections_util.node_parameters('NB_Generator',
        conf['nb_generator_node_ip'], int(conf['nb_generator_node_ssh_port']),
        conf['nb_generator_node_username'], conf['nb_generator_node_password'])

    # list of samples: each sample is a dictionary containing information that
    # describes a single measurement, i.e.:
    #    - the actual performance results
    #    - secondary runtime statistics
    #    - current values of test dimensions (dynamic)
    #    - test configuration options (static)
    total_samples = []
    java_opts = conf['java_opts']

    try:
        # Before proceeding with the experiments check validity
        # of all handlers
        logging.info('{0} checking controller/local multinet handler files.'.format(test_type))
        util.file_ops.check_filelist([
            controller_handlers_set.ctrl_build_handler,
            controller_handlers_set.ctrl_start_handler,
            controller_handlers_set.ctrl_status_handler,
            controller_handlers_set.ctrl_stop_handler,
            controller_handlers_set.ctrl_clean_handler,
            controller_handlers_set.ctrl_statistics_handler,
            controller_handlers_set.ctrl_change_persistent,
            multinet_local_handlers_set.build_handler,
            multinet_local_handlers_set.clean_handler])

        logging.info('{0} Cloning Multinet repository.'.format(test_type))
        multinet_utils.multinet_pre_post_actions(
                        multinet_local_handlers_set.build_handler)

        # Before proceeding with the experiments check validity
        # of all multinet handlers
        logging.info('{0} checking multinet handler files.'.format(test_type))
        util.file_ops.check_filelist([
            multinet_handlers_set.rest_server_boot,
            multinet_handlers_set.stop_switches_handler,
            multinet_handlers_set.get_switches_handler,
            multinet_handlers_set.init_topo_handler,
            multinet_handlers_set.start_topo_handler,
            multinet_handlers_set.rest_server_stop,
            multinet_handlers_set.get_flows_handler])

        # Opening connection with topology_node_ip and returning
        # controller_ssh_client, nb_generator_ssh_client to be utilized in the
        # sequel
        controller_ssh_client, nb_generator_ssh_client = \
            common.open_ssh_connections([controller_node, nb_generator_node])

        controller_cpus, nb_generator_cpus = common.create_cpu_shares(
            controller_cpu_shares, nb_generator_cpu_shares)

        # Controller common pre actions:
        # 1. rebuild controller if controller_rebuild is SET
        # 2. check_for_active controller,
        # 3. generate_controller_xml_files
        controller_utils.controller_pre_actions(controller_handlers_set,
                                      controller_rebuild, controller_ssh_client,
                                      java_opts, controller_sb_interface.port,
                                      controller_cpus)

        # Run tests for all possible dimensions
        for (total_flows,
             flow_operations_delay_ms,
             multinet_worker_topo_size,
             flow_workers,
             multinet_group_size,
             multinet_group_delay_ms,
             multinet_hosts_per_switch,
             multinet_topology_type,
             controller_statistics_period_ms) in \
             itertools.product(conf['total_flows'],
                               conf['flow_operations_delay_ms'],
                               conf['topology_size'],
                               conf['flow_workers'],
                               conf['topology_group_size'],
                               conf['topology_group_delay_ms'],
                               conf['topology_hosts_per_switch'],
                               conf['topology_type'],
                               conf['controller_statistics_period_ms']):

            logging.info('{0} changing controller statistics period to {1} ms'.
                format(test_type, controller_statistics_period_ms))
            controller_utils.controller_changestatsperiod(
                controller_handlers_set.ctrl_statistics_handler,
                controller_statistics_period_ms, controller_ssh_client)

            logging.info('{0} generating new configuration file'.format(test_type))
            multinet_utils.generate_multinet_config(controller_sb_interface,
                multinet_rest_server, multinet_node,
                multinet_worker_topo_size,
                multinet_group_size, multinet_group_delay_ms,
                multinet_hosts_per_switch, multinet_topology_type,
                multinet_switch_type, multinet_worker_ip_list,
                multinet_worker_port_list, multinet_base_dir, 0, 0)

            logging.info('{0} booting up Multinet REST server'.
                          format(test_type))
            multinet_utils.multinet_command_runner(multinet_handlers_set.rest_server_boot,
                'deploy_multinet', multinet_base_dir, is_privileged=False)

            logging.info('{0} starting controller'.format(test_type))
            cpid = controller_utils.start_controller(controller_handlers_set,
                controller_sb_interface.port, ' '.join(conf['java_opts']),
                controller_cpus, controller_ssh_client)

            logging.info('{0} OK, controller status is 1.'.format(test_type))

            logging.info(
                '{0} initializing topology on REST server.'.format(test_type))
            multinet_utils.multinet_command_runner(
                multinet_handlers_set.init_topo_handler,
                'init_topo_handler_multinet', multinet_base_dir)

            logging.info('{0} starting Multinet topology.'.format(test_type))
            multinet_utils.multinet_command_runner(
                multinet_handlers_set.start_topo_handler,
                'start_topo_handler_multinet', multinet_base_dir)

            logging.info('{0} Check if topology has successfully booted and '
                         'controller has identified all switches.'.
                         format(test_type))
            multinet_utils.check_topo_booted(
                multinet_worker_topo_size*multinet_workers,
                multinet_group_size, multinet_group_delay_ms,
                multinet_handlers_set.get_switches_handler,
                multinet_rest_server, controller_nb_interface,
                multinet_base_dir)


            # Check initial flows of booted switches
            logging.info('{0} Check initial operational DataStore flows and '
                         'topology switches flows.'.format(test_type))
            initial_operational_ds_flows = nb_utils.get_operational_ds_flows(
                controller_nb_interface)
            logging.info('{0} Checking for flows presence on controller operational datastore: {1}'.
                         format(test_type, initial_operational_ds_flows))
            initial_topology_flows = \
                multinet_utils.get_topology_flows(multinet_base_dir,
                                                  multinet_handlers_set.get_flows_handler)
            logging.info('{0} Checking for flows presence on topology switches: {1}'.
                         format(test_type, initial_topology_flows))
            if (initial_operational_ds_flows != 0 or initial_topology_flows != 0):
                raise ValueError('Initial installed flows were not equal to 0.')

            # start northbound generator flow_delete_flag SET
            add_failed_flows_operations = 0
            delete_failed_flows_operations = 0
            result_metrics_add = {}
            result_metrics_del = {}

            time_of_first_REST_request = time.time()

            nb_generator_start_json_output = \
                nb_utils.nb_generator_start(nb_generator_ssh_client,
                                        nb_generator_base_dir,nb_generator_cpus,
                                        nb_generator_handlers_set,controller_node,
                                        controller_nb_interface,total_flows,flow_workers,
                                        flow_operations_delay_ms,False,flows_per_request,log_level)
            nb_generator_start_output = json.loads(nb_generator_start_json_output)

            add_failed_flows_operations = nb_generator_start_output[0]
            add_controller_time = time.time() - time_of_first_REST_request

            result_metrics_add.update(nb_utils.monitor_threads_run(total_flows,
                                         time_of_first_REST_request,
                                         controller_nb_interface,
                                         multinet_handlers_set.get_flows_handler,multinet_base_dir))
            end_to_end_installation_time = result_metrics_add['end_to_end_flows_operation_time']
            add_switch_time = result_metrics_add['switch_operation_time']
            add_confirm_time = result_metrics_add['confirm_time']

            # start northbound generator flow_delete_flag SET
            if flow_delete_flag:
                time_of_first_REST_request = time.time()
                nb_generator_start_json_output = \
                    nb_utils.nb_generator_start(nb_generator_ssh_client,
                                            nb_generator_base_dir,nb_generator_cpus,
                                            nb_generator_handlers_set,controller_node,
                                            controller_nb_interface,total_flows,flow_workers,
                                            flow_operations_delay_ms,True,flows_per_request,log_level)
                nb_generator_start_output = json.loads(nb_generator_start_json_output)

                delete_failed_flows_operations = nb_generator_start_output[0]
                remove_controller_time = time.time() - time_of_first_REST_request

                result_metrics_del.update(nb_utils.monitor_threads_run(0,
                                         time_of_first_REST_request,
                                         controller_nb_interface,
                                         multinet_handlers_set.get_flows_handler,multinet_base_dir))
                end_to_end_remove_time = result_metrics_del['end_to_end_flows_operation_time']
                remove_switch_time = result_metrics_del['switch_operation_time']
                remove_confirm_time = result_metrics_del['confirm_time']


            total_failed_flows_operations = add_failed_flows_operations + \
                                            delete_failed_flows_operations


            # Results collection
            statistics = common.sample_stats(cpid, controller_ssh_client)
            statistics['global_sample_id'] = global_sample_id
            global_sample_id += 1
            statistics['multinet_workers'] = len(multinet_worker_ip_list)
            statistics['multinet_size'] = \
                multinet_worker_topo_size * len(multinet_worker_ip_list)
            statistics['multinet_topology_type'] = multinet_topology_type
            statistics['multinet_hosts_per_switch'] = \
                multinet_hosts_per_switch
            statistics['multinet_group_size'] = multinet_group_size
            statistics['multinet_group_delay_ms'] = multinet_group_delay_ms
            statistics['controller_node_ip'] = controller_node.ip
            statistics['controller_port'] = str(controller_sb_interface.port)
            statistics['controller_restart'] = controller_restart
            statistics['controller_cpu_shares'] = \
                '{0}'.format(controller_cpu_shares)
            statistics['total_flows'] = total_flows
            statistics['multinet_worker_topo_size'] = multinet_worker_topo_size
            statistics['controller_statistics_period_ms'] = \
                controller_statistics_period_ms
            statistics['nb_generator_cpu_shares'] = \
                '{0}'.format(nb_generator_cpu_shares)
            statistics['flow_operation_delay_ms'] = flow_operations_delay_ms
            statistics['flow_workers'] = flow_workers

            """
            # Flow scalability tests metrics
            # ------------------------------------------------------------------
            # Add controller time: Time for all ADD REST requests to be sent
                                   and their response to be received
            # 01. add_controller_time =
            # 02. add_controller_rate = Number of Flows / add_controller_time
            """
            statistics['add_controller_time'] = add_controller_time
            statistics['add_controller_rate'] = float(total_flows) / add_controller_time

            """
            # End-to-end-installation-time:
            # 03. end_to_end_installation_time =
            # 04. end_to_end_installation_rate = Number of Flows / end_to_end_installation_time
            """
            statistics['end_to_end_installation_time'] = end_to_end_installation_time
            if end_to_end_installation_time != -1:
                statistics['end_to_end_installation_rate'] = \
                    float(total_flows) / end_to_end_installation_time
            else:
                statistics['end_to_end_installation_rate'] = -1

            """
            # Add switch time: Time from the FIRST REST request until ALL flows
            #                  are present in the network
            # 05. add_switch_time =
            # 06. add_switch_rate =
            """
            statistics['add_switch_time'] = add_switch_time
            if add_switch_time != -1:
                statistics['add_switch_rate'] = float(total_flows) / add_switch_time
            else:
                statistics['add_switch_rate'] = -1

            """
            # Add confirm time: Time period started after the last flow was
                                configured until we receive “confirmation” all
                                flows are added.
            """
            # 07. add_confirm_time =
            # 08. add_confirm_rate =
            statistics['add_confirm_time'] = add_confirm_time
            if add_confirm_time != -1:
                statistics['add_confirm_rate'] = float(total_flows) / add_confirm_time
            else:
                statistics['add_confirm_rate'] = -1
            """
            # Remove controller time: Time for all delete REST
                                      requests to be sent and their response to
                                      be received
            # 09. remove_controller_time =
            # 10. remove_controller_rate

            # Remove switch time: Time from the first delete REST
                                  request until all flows are removed from the
                                  network.
            # 11. remove_switch_time =
            # 12. remove_switch_time =

            # Remove confirm time:
            # 13. remove_confirm_time = Time period started after the last
                                        flow was unconfigured until we receive
                                        “confirmation” all flows are removed.
            # 13. remove_confirm_rate =

            """

            if flow_delete_flag:
                statistics['remove_controller_time'] = remove_controller_time
                statistics['remove_controller_rate'] =  float(total_flows) / remove_controller_time

                statistics['end_to_end_remove_time'] = end_to_end_remove_time
                statistics['end_to_end_remove_rate'] = float(total_flows) / end_to_end_remove_time

                statistics['remove_switch_time'] = remove_switch_time
                statistics['remove_switch_rate'] = float(total_flows) / remove_switch_time

                statistics['remove_confirm_time'] = remove_confirm_time
                statistics['remove_confirm_rate'] = float(total_flows) / remove_confirm_time

            statistics['total_failed_flows_operations'] = total_failed_flows_operations

            statistics['flow_delete_flag'] = str(flow_delete_flag)
            total_samples.append(statistics)

            logging.debug('{0} stopping controller.'.format(test_type))
            controller_utils.stop_controller(controller_handlers_set, cpid,
                                             controller_ssh_client)

            logging.info('{0} stopping Multinet topology.'.format(test_type))
            multinet_utils.multinet_command_runner(
                multinet_handlers_set.stop_switches_handler,
                'stop_switches_handler_multinet', multinet_base_dir)

            logging.info('{0} stopping REST daemon in Multinet node'.
                format(test_type))

            multinet_utils.multinet_command_runner(
                multinet_handlers_set.rest_server_stop, 'cleanup_multinet',
                multinet_base_dir)

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
            controller_utils.stop_controller(controller_handlers_set, cpid,
                                             controller_ssh_client)
        except:
            pass

        try:
            logging.info('{0} collecting logs'.format(test_type))
            util.netutil.copy_dir_remote_to_local(controller_node,
                controller_logs_dir, output_dir+'/log')
        except:
            logging.error('{0} {1}'.format(
                test_type, 'failed transferring controller logs dir.'))

        if controller_cleanup:
            logging.info('{0} cleaning controller directory'.format(test_type))
            controller_utils.cleanup_controller(
                controller_handlers_set.ctrl_clean_handler,
                controller_ssh_client)

        try:
            logging.info(
                '{0} stopping REST daemon in Multinet node.'.
                format(test_type))
            multinet_utils.multinet_command_runner(
                multinet_handlers_set.rest_server_stop, 'cleanup_multinet',
                multinet_base_dir)
        except:
            pass

        logging.info('{0} Cleanup Multinet nodes.'.format(test_type))
        multinet_utils.multinet_pre_post_actions(
            multinet_local_handlers_set.clean_handler)

        # Closing ssh connections with controller/nb_generator nodes
        common.close_ssh_connections([controller_ssh_client,
                                      nb_generator_ssh_client])




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
             ('topology_rest_server_boot', 'Multinet boot handler'),
             ('topology_stop_switches_handler',
              'Multinet stop switches handler'),
             ('topology_get_switches_handler', 'Multinet get switches handler'),
             ('topology_init_handler',
              'Multinet initialize topology handler'),
             ('topology_start_switches_handler', 'Multinet start topology handler'),
             ('topology_node_ip', 'Multinet node IP'),
             ('topology_rest_server_port', 'Multinet node REST server port'),
             ('topology_size', 'Multinet network size per worker'),
             ('topology_type', 'Multinet topology type'),
             ('topology_hosts_per_switch', 'Multinet hosts per switch'),
             ('flow_workers', 'Flow worker threads'),
             ('total_flows', 'Total flows to be added'),
             ('flow_operations_delay_ms', 'Delay between flow operations'),
             ('flow_delete_flag', 'Flow delete flag'),
             ('flows_per_request', 'Flows per REST request'),
             ('java_opts', 'JVM options')], config_json)],
        [report_spec.TableSpec('2d', 'Test results',
            [('global_sample_id', 'Sample ID'),
             ('timestamp', 'Sample timestamp (seconds)'),
             ('date', 'Sample timestamp (date)'),
             ('total_flows', 'Total flow operations'),
             ('total_failed_flows_operations', 'Total failed flow operations'),
             ('add_controller_time',
              'Add controller time [s]'),
             ('add_controller_rate', 'Add controller rate [Flows/s]'),
             ('add_switch_time',
              'Add switch time [s]'),
             ('add_switch_rate', 'Add switch rate [Flows/s]'),
             ('add_confirm_time',
              'Add confirm time [s]'),
             ('add_confirm_rate', 'Add confirm rate [Flows/s]'),
             ('end_to_end_installation_time', 'End-to-end installation time [s]'),
             ('end_to_end_installation_rate',
              'End-to-end installation rate [Flows/s]'),
             ('remove_controller_time',
              'Total time of NB Restconf calls for flows deletion [s]'),
             ('remove_controller_rate', 'Remove controller rate [Flows/s]'),
             ('remove_switch_time', 'Remove switch time (seconds)'),
             ('remove_switch_rate', 'Remove switch rate (Flows/seconds)'),
             ('remove_confirm_time','Confirm time [s]'),
             ('remove_confirm_rate', 'Confirm rate [Flows/s]'),
             ('end_to_end_remove_time', 'Delete flows time [s]'),
             ('end_to_end_remove_rate', 'End-to-end remove rate [Flows/s]'),
             ('nb_generator_cpu_shares', 'NB traffic generator CPU percentage'),
             ('flow_operation_delay_ms', 'Flow operation delay [ms]'),
             ('flow_workers', 'Flow workers'),
             ('flow_delete_flag', 'Deletion flag'),
             ('multinet_size', 'Multinet Size'),
             ('multinet_worker_topo_size',
              'Topology size per Multinet worker'),
             ('multinet_workers','number of Multinet workers'),
             ('multinet_topology_type', 'Multinet topology Type'),
             ('multinet_hosts_per_switch', 'Multinet hosts per Switch'),
             ('multinet_group_size', 'Multinet group size'),
             ('multinet_group_delay_ms', 'Multinet group delay [ms]'),
             ('controller_node_ip', 'Controller IP node address'),
             ('controller_port', 'Controller port'),
             ('controller_vm_size', 'Controller VM size'),
             ('controller_java_xopts', 'Java options'),
             ('free_memory_bytes', 'System free memory [bytes]'),
             ('used_memory_bytes', 'System used memory [bytes]'),
             ('total_memory_bytes', 'System total memory [bytes]'),
             ('one_minute_load', 'One minute load'),
             ('five_minute_load', 'Five minutes load'),
             ('fifteen_minute_load', 'Fifteen minutes load'),
             ('controller_cpu_shares', 'Controller CPU percentage'),
             ('controller_cpu_system_time', 'Controller CPU system time'),
             ('controller_cpu_user_time', 'Controller CPU user time'),
             ('controller_num_threads', 'Controller num of threads'),
             ('controller_num_fds', 'Controller num of fds'),
             ('controller_statistics_period_ms',
              'Controller statistics period (ms)')], results_json)])

    return report_spec_obj
