# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Idle Southbound Performance test """

import common
import conf_collections_util
import controller_utils
import itertools
import logging
import multiprocessing
import multinet_utils
import oftraf_utils
import os
import report_spec
import sys
import time
import util.file_ops
import util.netutil

def sb_active_scalability_multinet_run(out_json, ctrl_base_dir,
                                       multinet_base_dir, conf, output_dir,
                                       oftraf_base_dir):
    """Run test. This is the main function that is called from
    nstat_orchestrator and performs the specific test.

    :param out_json: the JSON output file
    :param ctrl_base_dir: controller base directory
    :param multinet_base_dir: Multinet base directory
    :param conf: JSON configuration dictionary
    :param output_dir: directory to store output files
    :type out_json: str
    :type ctrl_base_dir: str
    :type multinet_base_dir: str
    :type conf: str
    :type output_dir: str
    """

    test_type = '[sb_active_multinet_scalability]'
    logging.info('{0} initializing test parameters'.format(test_type))

    # Global variables read-write shared between monitor-main thread.
    cpid = 0
    global_sample_id = 0

    t_start = multiprocessing.Value('d', 0.0)

    # Multinet parameters
    #multinet_hosts_per_switch = multiprocessing.Value('i', 0)
    #multinet_worker_topo_size = multiprocessing.Value('i', 0)
    multinet_worker_ip_list = conf['multinet_worker_ip_list']
    multinet_worker_port_list = conf['multinet_worker_port_list']

    # Controller parameters
    controller_logs_dir = ctrl_base_dir + conf['controller_logs_dir']
    controller_rebuild = conf['controller_rebuild']
    controller_cleanup = conf['controller_cleanup']
    if 'controller_cpu_shares' in conf:
        controller_cpu_shares = conf['controller_cpu_shares']
    else:
        controller_cpu_shares = 100
    multinet_switch_type = conf['multinet_switch_type']

    controller_handlers_set = conf_collections_util.controller_handlers(
        ctrl_base_dir + conf['controller_build_handler'],
        ctrl_base_dir + conf['controller_start_handler'],
        ctrl_base_dir + conf['controller_status_handler'],
        ctrl_base_dir + conf['controller_stop_handler'],
        ctrl_base_dir + conf['controller_clean_handler'],
        ctrl_base_dir + conf['controller_statistics_handler'],
        ctrl_base_dir + conf['controller_flowmods_conf_handler']
        )
    multinet_handlers_set = conf_collections_util.topology_generator_handlers(
        multinet_base_dir + conf['topology_rest_server_boot'],
        multinet_base_dir + conf['topology_stop_switches_handler'],
        multinet_base_dir + conf['topology_get_switches_handler'],
        multinet_base_dir + conf['topology_init_handler'],
        multinet_base_dir + conf['topology_start_switches_handler'],
        multinet_base_dir + conf['topology_rest_server_stop'],
        multinet_base_dir + conf['topology_traffic_gen_handler']
        )

    multinet_local_handlers_set = \
        conf_collections_util.multinet_local_handlers(
        multinet_base_dir + conf['multinet_build_handler'],
        multinet_base_dir + conf['multinet_clean_handler'])

    controller_node = conf_collections_util.node_parameters('Controller',
        conf['controller_node_ip'], int(conf['controller_node_ssh_port']),
        conf['controller_node_username'], conf['controller_node_password'])
    multinet_node = conf_collections_util.node_parameters('Multinet',
        conf['topology_node_ip'], int(conf['topology_node_ssh_port']),
        conf['topology_node_username'], conf['topology_node_password'])
    controller_sb_interface = conf_collections_util.controller_southbound(
        conf['controller_node_ip'], conf['controller_port'])
    multinet_rest_server = conf_collections_util.multinet_server(
        conf['topology_node_ip'], conf['topology_rest_server_port'])

    # Check if this is an oftraf test
    oftraf_rest_server = conf_collections_util.oftraf_server(
        conf['controller_node_ip'], conf['oftraf_rest_server_port'])
    oftraf_handlers_set = conf_collections_util.oftraf_handlers(
        oftraf_base_dir + 'build.sh', oftraf_base_dir + 'start.sh',
        oftraf_base_dir + 'stop.sh', oftraf_base_dir + 'clean.sh')
    #oftraf_test_interval_ms = conf['oftraf_test_interval_ms']

    # list of samples: each sample is a dictionary that contains
    # all information that describes a single measurement, i.e.:
    #    - the actual performance results
    #    - secondary runtime statistics
    #    - current values of test dimensions (dynamic)
    #    - test configuration options (static)
    total_samples = []
    java_opts = conf['java_opts']

    try:

        # Before proceeding with the experiments check validity
        # of all handlers
        logging.info('{0} checking controller/local multinet handler files.'.
                     format(test_type))
        util.file_ops.check_filelist([
            controller_handlers_set.ctrl_build_handler,
            controller_handlers_set.ctrl_start_handler,
            controller_handlers_set.ctrl_status_handler,
            controller_handlers_set.ctrl_stop_handler,
            controller_handlers_set.ctrl_clean_handler,
            controller_handlers_set.ctrl_statistics_handler,
            controller_handlers_set.ctrl_flowmods_conf_handler,
            multinet_local_handlers_set.build_handler,
            multinet_local_handlers_set.clean_handler,
            oftraf_handlers_set.oftraf_build_handler,
            oftraf_handlers_set.oftraf_start_handler,
            oftraf_handlers_set.oftraf_stop_handler,
            oftraf_handlers_set.oftraf_clean_handler])

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
            multinet_handlers_set.topology_traffic_gen_handler])

        # Opening connection with controller node and returning
        # ontroller_ssh_client to be utilized in the sequel
        controller_ssh_client = common.open_ssh_connections([controller_node])[0]

        controller_cpus = common.create_cpu_shares(
            controller_cpu_shares, 100)[0]

        # Controller common actions: rebuild controller if controller_rebuild is
        # SET, check_for_active controller, generate_controller_xml_files
        controller_utils.controller_pre_actions(controller_handlers_set,
                                      controller_rebuild, controller_ssh_client,
                                      java_opts, controller_sb_interface.port,
                                      controller_cpus)

        logging.info('{0} Configure controller to send FLOW_MODs as a response '
                     'to ARP PACKET_INs.'.format(test_type))
        controller_utils.flowmod_configure_controller(
            controller_handlers_set.ctrl_flowmods_conf_handler,
            controller_ssh_client)
        """
        logging.info('{0} Building oftraf.'.format(test_type))
        oftraf_utils.oftraf_build(oftraf_handlers_set.oftraf_build_handler,
                                  controller_ssh_client)
        """

        # Run tests for all possible dimensions
        for (multinet_worker_topo_size,
             multinet_group_size,
             multinet_group_delay_ms,
             multinet_hosts_per_switch,
             multinet_topology_type,
             controller_statistics_period_ms) in \
             itertools.product(conf['topology_size'],
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
                multinet_rest_server, multinet_node, multinet_worker_topo_size,
                multinet_group_size, multinet_group_delay_ms,
                multinet_hosts_per_switch, multinet_topology_type,
                multinet_switch_type, multinet_worker_ip_list,
                multinet_worker_port_list, multinet_base_dir)

            logging.info('{0} Starting oftraf traffic monitor in REST '
                         'server mode.'.format(test_type))
            oftraf_utils.oftraf_start(oftraf_handlers_set.oftraf_start_handler,
                controller_sb_interface, oftraf_rest_server.port,
                controller_ssh_client)

            logging.info('{0} starting controller'.format(test_type))
            cpid = controller_utils.start_controller(controller_handlers_set,
                controller_sb_interface.port, ' '.join(conf['java_opts']),
                controller_cpus, controller_ssh_client)

            # Control of controller status
            # is done inside controller_utils.start_controller()
            logging.info('{0} OK, controller status is 1.'.format(test_type))

            logging.info('{0} booting up Multinet REST server'.
                          format(test_type))

            multinet_utils.multinet_command_runner(multinet_handlers_set.rest_server_boot,
                'deploy_multinet', multinet_base_dir, is_privileged=False)

            logging.info(
                '{0} initiating topology on REST server and start '
                'monitor thread to check for discovered switches '
                'on controller.'.format(test_type))

            logging.info('{0} initializing Multinet topology.'.
                         format(test_type))

            multinet_utils.multinet_command_runner(
                multinet_handlers_set.init_topo_handler,
                'init_topo_handler_multinet', multinet_base_dir)

            t_start.value = time.time()

            logging.info('{0} starting Multinet topology.'.format(test_type))
            multinet_utils.multinet_command_runner(
                multinet_handlers_set.start_topo_handler,
                'start_topo_handler_multinet', multinet_base_dir)

            logging.info('{0} generating traffic from Multinet topology.'.format(test_type))
            multinet_utils.multinet_command_runner(
                multinet_handlers_set.topology_traffic_gen_handler,
                'topology_traffic_gen_handler_multinet', multinet_base_dir)

            # Parallel section.
            # We have boot_up_time equal to 0 because start_mininet_topo()
            # is a blocking function and topology is booted up after we have
            # call it
            logging.info('{0} creating queue'.format(test_type))
            result_queue = multiprocessing.Queue()

            # Parallel section.
            logging.info('{0} creating idle stability with oftraf '
                         'monitor thread'.format(test_type))
            monitor_thread = multiprocessing.Process(
                target=oftraf_utils.oftraf_monitor_thread,
                args=(0, oftraf_rest_server, result_queue))

            monitor_thread.start()
            res = result_queue.get(block=True)
            logging.info('{0} joining monitor thread'.format(test_type))
            monitor_thread.join()

            statistics = common.sample_stats(cpid, controller_ssh_client)
            statistics['global_sample_id'] = global_sample_id
            global_sample_id += 1
            statistics['multinet_workers'] = len(multinet_worker_ip_list)
            statistics['multinet_size'] = \
                multinet_worker_topo_size * len(multinet_worker_ip_list)
            statistics['multinet_worker_topo_size'] = multinet_worker_topo_size
            statistics['multinet_topology_type'] = multinet_topology_type
            statistics['multinet_hosts_per_switch'] = \
                multinet_hosts_per_switch
            statistics['multinet_group_size'] = multinet_group_size
            statistics['multinet_group_delay_ms'] = multinet_group_delay_ms
            statistics['controller_statistics_period_ms'] = \
                controller_statistics_period_ms
            statistics['controller_node_ip'] = controller_node.ip
            statistics['controller_port'] = str(controller_sb_interface.port)
            statistics['controller_cpu_shares'] = \
                '{0}'.format(controller_cpu_shares)
            statistics['of_out_packets_per_sec'] = res[0]
            statistics['of_out_bytes_per_sec'] = res[1]

            total_samples.append(statistics)

            logging.debug('{0} stopping controller.'.format(test_type))
            controller_utils.stop_controller(controller_handlers_set, cpid,
                                             controller_ssh_client)

            logging.info('{0} stopping Multinet topology.'.format(test_type))
            multinet_utils.multinet_command_runner(
                multinet_handlers_set.stop_switches_handler,
                'stop_switches_handler_multinet', multinet_base_dir)

            logging.info('{0} stopping oftraf REST server.'.
                         format(test_type))
            oftraf_utils.oftraf_stop(
                oftraf_handlers_set.oftraf_stop_handler,
                oftraf_rest_server, controller_ssh_client)

            logging.info('{0} stopping REST daemon in Multinet node'.
                format(test_type))

            multinet_utils.multinet_command_runner(
                multinet_handlers_set.rest_server_stop, 'cleanup_multinet',
                multinet_base_dir, is_privileged=True)

    except:
        logging.error('{0} :::::::::: Exception :::::::::::'.format(test_type))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error('{0} Exception: {1}, {2}'.
                      format(test_type, exc_type, exc_tb.tb_lineno))

        errors = str(exc_obj).rstrip().split('\n')
        for error in errors:
            logging.error('{0} {1}'.format(test_type, error))
        logging.exception('')

    finally:
        logging.info('{0} finalizing test'.format(test_type))

        logging.info('{0} creating test output directory if not exist.'.
                     format(test_type))
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        logging.info('{0} saving results to JSON file.'.format(test_type))
        common.generate_json_results(total_samples, out_json)

        try:
            logging.info('{0} stopping controller.'.
                         format(test_type))
            controller_utils.stop_controller( controller_handlers_set, cpid,
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
            #mininet_utils.stop_mininet_server(mininet_ssh_client,
            #                                  mininet_rest_server.port)
        except:
            pass

        try:
            logging.info('{0} stopping oftraf REST server.'.
                         format(test_type))
            oftraf_utils.oftraf_stop(
                oftraf_handlers_set.oftraf_stop_handler,
                oftraf_rest_server, controller_ssh_client)

        except:
            pass

        logging.info('{0} Cleanup Multinet nodes.'.format(test_type))
        multinet_utils.multinet_pre_post_actions(
            multinet_local_handlers_set.clean_handler)

        # Closing ssh connections with controller/Multinet nodes
        common.close_ssh_connections([controller_ssh_client])


def get_report_spec(test_type, config_json, results_json):
    """It returns all the information that is needed for the generation of the
    report for the specific test.

    :param test_type: Describes the type of the specific test. This value
    defines the title of the html report.
    :param config_json: this is the filepath to the configuration json file.
    :param results_json: this is the filepath to the results json file.
    :returns: A ReportSpec object that holds all the test report information
    and is passed as input to the generate_html() function in the
    html_generation.py, that is responsible for the report generation.
    :rtype: ReportSpec
    :type: test_type: str
    :type: config_json: str
    :type: results_json: str
    """

    report_spec_obj = report_spec.ReportSpec(config_json, results_json,
        '{0}'.format(test_type), [report_spec.TableSpec('1d',
            'Test configuration parameters (detailed)',
            [('test_repeats', 'Test repeats'),
             ('controller_name', 'Controller name'),
             ('controller_build_handler', 'Controller build script'),
             ('controller_start_handler', 'Controller start script'),
             ('controller_stop_handler', 'Controller stop script'),
             ('controller_status_handler', 'Controller status script'),
             ('controller_clean_handler', 'Controller cleanup script'),
             ('controller_statistics_handler', 'Controller statistics script'),
             ('controller_node_ip', 'Controller IP node address'),
             ('controller_node_ssh_port', 'Controller node ssh port'),
             ('controller_node_username', 'Controller node username'),
             ('controller_node_password', 'Controller node password'),
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
             ('topology_node_ip', 'Multinet IP address'),
             ('topology_rest_server_port', 'Multinet port'),
             ('topology_size', 'Multinet network size per worker'),
             ('topology_type', 'Multinet topology type'),
             ('topology_hosts_per_switch', 'Multinet hosts per switch'),
             ('java_opts', 'JVM options')], config_json)],
        [report_spec.TableSpec('2d', 'Test results',
            [('global_sample_id', 'Sample ID'),
             ('timestamp', 'Sample timestamp (seconds)'),
             ('date', 'Sample timestamp (date)'),
             ('bootup_time_secs', 'Time to discover switches (seconds)'),
             ('discovered_switches', 'Discovered switches'),
             ('multinet_size', 'Multinet Size'),
             ('multinet_worker_topo_size',
              'Topology size per Multinet worker'),
             ('multinet_workers','number of Multinet workers'),
             ('multinet_topology_type', 'Multinet topology Type'),
             ('multinet_hosts_per_switch', 'Multinet hosts per Switch'),
             ('multinet_group_size', 'Multinet group size'),
             ('multinet_group_delay_ms', 'Multinet group delay (ms)'),
             ('controller_node_ip', 'Controller IP'),
             ('controller_port', 'Controller port'),
             ('controller_java_xopts', 'Java options'),
             ('one_minute_load', 'One minute load'),
             ('five_minute_load', 'five minutes load'),
             ('fifteen_minute_load', 'fifteen minutes load'),
             ('used_memory_bytes', 'System used memory (Bytes)'),
             ('total_memory_bytes', 'Total system memory'),
             ('controller_cpu_shares', 'Controller CPU percentage'),
             ('controller_cpu_system_time', 'Controller CPU system time'),
             ('controller_cpu_user_time', 'Controller CPU user time'),
             ('controller_num_threads', 'Controller threads'),
             ('controller_num_fds', 'Controller num of fds'),
             ('controller_statistics_period_ms',
              'Controller Statistics Period (ms)')], results_json)])

    return report_spec_obj
