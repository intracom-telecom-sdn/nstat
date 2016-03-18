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
import mininet_utils
import os
import report_spec
import sys
import util.file_ops
import util.netutil


def nb_active_scalability_mininet_run(out_json, ctrl_base_dir,
                                      nb_generator_base_dir, mininet_base_dir,
                                      conf, output_dir, log_level):

    """Run northbound active test with Mininet.

    :param out_json: the JSON output file
    :param ctrl_base_dir: controller base directory
    :param nb_generator_base_dir: northbound generator base directory
    :param mininet_base_dir: Mininet base directory
    :param conf: JSON configuration dictionary
    :param output_dir: directory to store output files
    :param log_level: This parameter is used in order to pass NSTAT
    --logging-level argument to NorthBound generator.
    :type out_json: str
    :type ctrl_base_dir: str
    :type nb_generator_base_dir: str
    :type mininet_base_dir: str
    :type conf: dict
    :type output_dir: str
    :type log_level: str
    """

    test_type = '[nb_active_scalability_mininet]'
    logging.info('{0} initializing test parameters.'.format(test_type))

    # Global variables read-write shared between monitor and main thread
    global_sample_id = 0
    cpid = 0
    flow_delete_flag = conf['flow_delete_flag']

    # Northbound generator node parameters
    if 'nb_generator_cpu_shares' in conf:
        nb_generator_cpu_shares = conf['nb_generator_cpu_shares']

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
        ''
        )
    mininet_handlers_set = conf_collections_util.topology_generator_handlers(
        mininet_base_dir + conf['topology_rest_server_boot'],
        mininet_base_dir + conf['topology_stop_switches_handler'],
        mininet_base_dir + conf['topology_get_switches_handler'],
        mininet_base_dir + conf['topology_init_handler'],
        mininet_base_dir + conf['topology_start_switches_handler'],
        mininet_base_dir + conf['topology_rest_server_stop'], ''
        )
    nb_generator_handlers_set = conf_collections_util.nb_generator_handlers(
        nb_generator_base_dir + conf['nb_generator_run_handler'])
    controller_node = conf_collections_util.node_parameters('Controller',
        conf['controller_node_ip'], int(conf['controller_node_ssh_port']),
        conf['controller_node_username'], conf['controller_node_password'])
    mininet_node = conf_collections_util.node_parameters('Mininet',
        conf['topology_node_ip'], int(conf['topology_node_ssh_port']),
        conf['topology_node_username'], conf['topology_node_password'])
    controller_sb_interface = conf_collections_util.controller_southbound(
        conf['controller_node_ip'], conf['controller_port'])
    controller_nb_interface = conf_collections_util.controller_northbound(
        conf['controller_node_ip'], conf['controller_restconf_port'],
        conf['controller_restconf_user'], conf['controller_restconf_password'])
    mininet_rest_server = conf_collections_util.mininet_server(
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
        # check validity of all handlers
        util.file_ops.check_filelist([
            controller_handlers_set.ctrl_build_handler,
            controller_handlers_set.ctrl_start_handler,
            controller_handlers_set.ctrl_status_handler,
            controller_handlers_set.ctrl_stop_handler,
            controller_handlers_set.ctrl_clean_handler,
            controller_handlers_set.ctrl_statistics_handler,
            mininet_handlers_set.rest_server_boot,
            mininet_handlers_set.stop_switches_handler,
            mininet_handlers_set.get_switches_handler,
            mininet_handlers_set.init_topo_handler,
            mininet_handlers_set.start_topo_handler,
            ])

        # opening connection with topology_node_ip and returning
        # mininet_ssh_client to be utilized in the sequel
        mininet_ssh_client, controller_ssh_client, nb_generator_ssh_client = \
            common.open_ssh_connections([mininet_node,
                controller_node, nb_generator_node])

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
             topology_size,
             flow_workers,
             topology_group_size,
             topology_group_delay_ms,
             topology_hosts_per_switch,
             topology_type,
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

            logging.info('{0} booting up Mininet REST server'.
                          format(test_type))
            mininet_utils.start_mininet_server(mininet_ssh_client,
                mininet_handlers_set.rest_server_boot, mininet_rest_server)

            logging.info('{0} starting controller'.format(test_type))
            cpid = controller_utils.start_controller(controller_handlers_set,
                controller_sb_interface.port, ' '.join(conf['java_opts']),
                controller_cpus, controller_ssh_client)

            logging.info('{0} OK, controller status is 1.'.format(test_type))

            logging.info(
                '{0} initializing topology on REST server.'.format(test_type))
            mininet_utils.init_mininet_topo(
                mininet_handlers_set.init_topo_handler, mininet_rest_server,
                controller_sb_interface.ip, controller_sb_interface.port,
                topology_type, topology_size, topology_group_size,
                topology_group_delay_ms, topology_hosts_per_switch)

            logging.info('{0} starting Mininet topology.'.format(test_type))
            mininet_utils.start_stop_mininet_topo(
                mininet_handlers_set.start_topo_handler, mininet_rest_server,
                'start')

            common.check_topo_booted(topology_size, topology_group_size,
                                     topology_group_delay_ms,
                                     mininet_handlers_set.get_switches_handler,
                                     mininet_rest_server,
                                     controller_nb_interface)


            cmd = ('cd {0}; taskset -c {1} python3.4 {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}'.
                format(nb_generator_base_dir, nb_generator_cpus,
                       nb_generator_handlers_set.run_handler,
                       controller_node.ip, controller_nb_interface.port,
                       total_flows, flow_workers, flow_operations_delay_ms,
                       flow_delete_flag, controller_nb_interface.username,
                       controller_nb_interface.password, log_level))
            logging.debug('{0} Generator handler command:{1}.'.
                          format(test_type, cmd))

            exit_status , output = util.netutil.ssh_run_command(
                nb_generator_ssh_client, cmd , '[generator_run_handler]')

            if exit_status!=0:
                raise Exception('{0} northbound generator failed'.
                                format(test_type))

            results = json.loads(output)

            # Results collection
            statistics = common.sample_stats(cpid, controller_ssh_client)
            statistics['global_sample_id'] = global_sample_id
            global_sample_id += 1
            statistics['controller_node_ip'] = controller_node.ip
            statistics['controller_port'] = str(controller_sb_interface.port)
            statistics['controller_restart'] = controller_restart
            statistics['controller_cpu_shares'] = \
                '{0}'.format(controller_cpu_shares)
            statistics['total_flows'] = total_flows
            statistics['topology_size'] = topology_size
            statistics['topology_type'] = topology_type
            statistics['topology_hosts_per_switch'] = \
                topology_hosts_per_switch
            statistics['topology_group_size'] = topology_group_size
            statistics['topology_group_delay_ms'] = topology_group_delay_ms
            statistics['controller_statistics_period_ms'] = \
                controller_statistics_period_ms
            statistics['nb_generator_cpu_shares'] = \
                '{0}'.format(nb_generator_cpu_shares)
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

            logging.debug('{0} stopping controller.'.format(test_type))
            controller_utils.stop_controller(controller_handlers_set, cpid,
                                             controller_ssh_client)

            logging.info('{0} stopping Mininet topology.'.format(test_type))
            mininet_utils.start_stop_mininet_topo(
                mininet_handlers_set.stop_switches_handler,
                mininet_rest_server, 'stop')

            logging.info('{0} stopping REST daemon in Mininet node'.
                format(test_type))
            mininet_utils.stop_mininet_server(mininet_ssh_client,
                                              mininet_rest_server.port)

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
            logging.info('{0} stopping REST daemon in Mininet node.'.
                          format(test_type))
            mininet_utils.stop_mininet_server(mininet_ssh_client,
                                              mininet_rest_server.port)
        except:
            pass

        # Closing ssh connections with controller/Mininet/nb_generator nodes
        common.close_ssh_connections([controller_ssh_client,
                                      mininet_ssh_client,
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
             ('topology_rest_server_boot', 'Mininet boot handler'),
             ('topology_stop_switches_handler',
              'Mininet stop switches handler'),
             ('topology_get_switches_handler', 'Mininet get switches handler'),
             ('topology_init_handler',
              'Mininet initialize topology handler'),
             ('topology_start_switches_handler', 'Mininet start topology handler'),
             ('topology_node_ip', 'Mininet node IP'),
             ('topology_rest_server_port', 'Mininet node REST server port'),
             ('topology_size', 'Mininet network size'),
             ('topology_type', 'Mininet topology type'),
             ('topology_hosts_per_switch', 'Mininet hosts per switch'),
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
             ('nb_generator_cpu_shares', 'NB traffic generator CPU percentage'),
             ('flow_operation_delay_ms', 'Flow operation delay (milliseconds)'),
             ('flow_workers', 'Flow workers'),
             ('flow_delete_flag', 'Deletion flag'),
             ('topology_size', 'Mininet Size'),
             ('topology_type', 'Mininet Topology Type'),
             ('topology_hosts_per_switch', 'Mininet Hosts per Switch'),
             ('topology_group_size', 'Mininet Group Size'),
             ('topology_group_delay_ms', 'Mininet Group Delay (ms)'),
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
             ('controller_cpu_shares', 'Controller CPU percentage'),
             ('controller_cpu_system_time', 'Controller CPU system time'),
             ('controller_cpu_user_time', 'Controller CPU user time'),
             ('controller_num_threads', 'Controller num of threads'),
             ('controller_num_fds', 'Controller num of fds'),
             ('controller_statistics_period_ms',
              'Controller statistics period (ms)')], results_json)])

    return report_spec_obj
