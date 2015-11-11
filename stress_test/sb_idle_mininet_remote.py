# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Idle Southbound Performance test """

import common
import controller_utils
import itertools
import json
import logging
import mininet_utils
import multiprocessing
import os
import report_spec
import shutil
import sys
import time
import util.customsubprocess
import util.file_ops
import util.process
import util.netutil

def sb_idle_mininet_run(out_json, ctrl_base_dir, mininet_base_dir, conf,
                        output_dir):
    """Run test. This is the main function that is called from
    nstat_orchestrator and performs the specific test.

    :param out_json: the JSON output file
    :param ctrl_base_dir: controller base directory
    :param mininet_base_dir: mininet base directory
    :param conf: JSON configuration dictionary
    :param output_dir: directory to store output files
    :type out_json: str
    :type ctrl_base_dir: str
    :type mininet_base_dir: str
    :type conf: str
    :type output_dir: str
    """

    # Global variables read-write shared between monitor-main thread.
    cpid = 0
    global_sample_id = 0
    test_type = '[sb_idle_mininet]'

    logging.info('{0} Initializing test parameters'.format(test_type))
    controller_build_handler = ctrl_base_dir + conf['controller_build_handler']
    controller_start_handler = ctrl_base_dir + conf['controller_start_handler']
    controller_status_handler = \
        ctrl_base_dir + conf['controller_status_handler']
    controller_stop_handler = ctrl_base_dir + conf['controller_stop_handler']
    controller_clean_handler = ctrl_base_dir + conf['controller_clean_handler']
    controller_statistics_handler = \
        ctrl_base_dir + conf['controller_statistics_handler']
    controller_logs_dir = ctrl_base_dir + conf['controller_logs_dir']

    controller_node_ip = multiprocessing.Array('c',
        str(conf['controller_node_ip']).encode())
    controller_node_ssh_port = conf['controller_node_ssh_port']
    controller_restconf_user = multiprocessing.Array('c',
        str(conf['controller_restconf_user']).encode())

    controller_restconf_password = multiprocessing.Array('c',
        str(conf['controller_restconf_password']).encode())


    controller_port = conf['controller_port']
    controller_restconf_port = multiprocessing.Value('i',
        conf['controller_restconf_port'])

    controller_restconf_auth_token = (conf['controller_restconf_user'],
                                      conf['controller_restconf_password'])
    controller_rebuild = conf['controller_rebuild']

    controller_cleanup = conf['controller_cleanup']


    mininet_boot_handler = mininet_base_dir + conf['mininet_boot_handler']
    mininet_stop_switches_handler = mininet_base_dir + \
        conf['mininet_stop_switches_handler']
    mininet_get_switches_handler = mininet_base_dir + \
        conf['mininet_get_switches_handler']
    mininet_init_topo_handler = mininet_base_dir + \
        conf['mininet_init_topo_handler']
    mininet_start_topo_handler = mininet_base_dir + \
        conf['mininet_start_topo_handler']
    mininet_size = multiprocessing.Value('i', conf['mininet_size'])

    mininet_server_remote_path = mininet_base_dir + '/mininet_custom_boot.py'
    mininet_node_ip = conf['mininet_node_ip']
    mininet_node_ssh_port = conf['mininet_node_ssh_port']
    mininet_server_rest_port = conf['mininet_server_rest_port']
    mininet_node_username = conf['mininet_node_username']
    mininet_node_password = conf['mininet_node_password']

    t_start = multiprocessing.Value('d', 0.0)
    bootup_time_ms = multiprocessing.Value('i', 0)
    discovery_deadline_ms.value = multiprocessing.Value('i', 0)
    cbench_switches = multiprocessing.Value('i', 0)

    # list of samples: each sample is a dictionary that contains
    # all information that describes a single measurement, i.e.:
    #    - the actual performance results
    #    - secondary runtime statistics
    #    - current values of test dimensions (dynamic)
    #    - test configuration options (static)
    total_samples = []

    try:
        # Before procceeding with the experiments check validity
        # of all handlers
        util.file_ops.check_filelist([controller_build_handler,
            controller_start_handler, controller_status_handler,
            controller_stop_handler, controller_clean_handler,
            controller_statistics_handler, mininet_boot_handler,
            mininet_stop_switches_handler, mininet_get_switches_handler,
            mininet_start_topo_handler, mininet_init_topo_handler])

        # Opening connection with mininet_node_ip and returning
        # mininet_ssh_client to be utilized in the sequel
        logging.info('{0} Initiating session with Mininet VM.'.
                     format(test_type))
        mininet_ssh_client = util.netutil.ssh_connect_or_return(mininet_node_ip,
            mininet_node_username, mininet_node_password, 10,
            mininet_node_ssh_port)

        # Opening connection with controller_node_ip and returning
        # controller_ssh_client to be utilized in the sequel
        controller_ssh_client = util.netutil.ssh_connect_or_return(
            controller_node_ip.value.decode(),
            controller_node_username.value.decode(),
            controller_node_password.value.decode(), 10,
            int(controller_node_ssh_port.value.decode()))


        if controller_rebuild:
            logging.info('{0} Building controller'.format(test_type))
            controller_utils.rebuild_controller(controller_build_handler,
                                                controller_ssh_client)

        controller_utils.check_for_active_controller(controller_port,
                                                     controller_ssh_client)
        logging.info(
            '{0} Starting and stopping controller to generate xml files'.
            format(test_type))

        cpid = controller_utils.start_controller(
            controller_start_handler, controller_status_handler,
            controller_port.value, ' '.join(conf['java_opts']),
            controller_ssh_client)

        # Controller status check is done inside start_controller() of the
        # controller_utils
        logging.info('{0} OK, controller status is 1.'.format(test_type))
        controller_utils.stop_controller(controller_stop_handler,
            controller_status_handler, cpid, controller_ssh_client)

        # Run tests for all possible dimensions
        for (mininet_size.value,
             mininet_group_size,
             mininet_group_delay_ms,
             mininet_hosts_per_switch,
             mininet_topology_type,
             controller_statistics_period_ms) in \
             itertools.product(conf['mininet_size'],
                               conf['mininet_group_size'],
                               conf['mininet_group_delay_ms'],
                               conf['mininet_hosts_per_switch'],
                               conf['mininet_topology_type'],
                               conf['controller_statistics_period_ms']):

            controller_utils.controller_changestatsperiod(
                controller_statistics_handler, controller_statistics_period_ms,
                controller_ssh_client)

            logging.info('{0} Booting up Mininet REST server'.
                          format(test_type))
            mininet_utils.start_mininet_server(mininet_ssh_client,
                mininet_server_remote_path, mininet_node_ip,
                mininet_server_rest_port)

            logging.info('{0} Starting controller'.format(test_type))
            cpid = controller_utils.start_controller(
                controller_start_handler, controller_status_handler,
                controller_port.value, ' '.join(conf['java_opts']),
                controller_ssh_client)
            # Control of controller status
            # is done inside controller_utils.start_controller()
            logging.info('{0} OK, controller status is 1.'.format(test_type))

            logging.debug('{0} Creating queue'.format(test_type))

            result_queue = multiprocessing.Queue()

            sleep_ms = \
                int(mininet_size.value/mininet_group_size) * mininet_group_delay_ms
            total_mininet_hosts = mininet_hosts_per_switch * mininet_size.value

            # We want this value to be big, equivalent to the topology size.
            discovery_deadline_ms.value = \
                (7000 * (mininet_size.value + total_mininet_hosts)) + sleep_ms

            logging.info(
                '{0} Initiating topology on REST server and start '
                'monitor thread to check for discovered switches '
                'on controller.'.format(test_type))
            logging.info('{0} Initialize mininet topology.'.format(test_type))
            mininet_utils.init_mininet_topo(mininet_init_topo_handler,
                mininet_node_ip, mininet_server_rest_port, controller_node_ip,
                controller_port, mininet_topology_type, mininet_size.value,
                mininet_group_size, mininet_group_delay_ms,
                mininet_hosts_per_switch)

            t_start = time.time()

            logging.debug('{0} Start mininet topology.'.format(test_type))
            mininet_utils.start_mininet_topo(mininet_start_topo_handler,
                mininet_node_ip, mininet_server_rest_port)

            # Parallel section
            logging.info('{0} Creating monitor thread'.format(test_type))
            monitor_thread = multiprocessing.Process(
                target=common.poll_ds_thread,
                args=(controller_node_ip, controller_restconf_port,
                      controller_restconf_user,
                      controller_restconf_password,
                      t_start, bootup_time_ms, mininet_size,
                      discovery_deadline_ms, result_queue))

            monitor_thread.start()
            res = result_queue.get(block=True)

            logging.info('{0} Joining monitor thread'.format(test_type))
            monitor_thread.join()

            statistics = common.sample_stats(cpid)
            statistics['global_sample_id'] = global_sample_id
            global_sample_id += 1
            statistics['mininet_size'] = mininet_size.value
            statistics['mininet_topology_type'] = mininet_topology_type
            statistics['mininet_hosts_per_switch'] = \
                mininet_hosts_per_switch
            statistics['mininet_group_size'] = mininet_group_size
            statistics['mininet_group_delay_ms'] = mininet_group_delay_ms
            statistics['controller_statistics_period_ms'] = \
                controller_statistics_period_ms
            statistics['controller_node_ip'] = controller_node_ip
            statistics['controller_port'] = str(controller_port)
            statistics['bootup_time_secs'] = res[1]
            statistics['discovered_switches'] = res[2]
            total_samples.append(statistics)

            logging.info('{0} Stopping mininet topology.'.format(test_type))
            mininet_utils.stop_mininet_topo(mininet_stop_switches_handler,
                mininet_node_ip, mininet_server_rest_port)

            controller_utils.stop_controller(controller_stop_handler,
                controller_status_handler, cpid, controller_ssh_client)

            logging.info(
                '{0} Killing REST daemon in Mininet VM and existing topology.'.
                format(test_type))
            mininet_utils.stop_mininet_server(mininet_ssh_client,
                                              mininet_server_rest_port)

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
        logging.info('{0} Finalizing test'.format(test_type))

        logging.info('{0} Creating test output directory if not exist.'.
                     format(test_type))
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if len(total_samples) > 0:
            with open(out_json, 'w') as ojf:
                json.dump(total_samples, ojf)
            ojf.close()

        try:
            logging.info('{0} Stopping controller.'.
                         format(test_type))
            controller_utils.stop_controller(controller_stop_handler,
                controller_status_handler, cpid, controller_ssh_client)
        except:
            pass

        try:
            logging.info('{0} Collecting logs'.format(test_type))
            util.netutil.copy_remote_directory(
                controller_node_ip.value.decode(),
                controller_node_username.value.decode(),
                controller_node_password.value.decode(),
                controller_logs_dir, output_dir+'/log',
                int(controller_node_ssh_port.value.decode()))
        except:
            logging.error('{0} {1}'.format(
                test_type, 'Fail to transfer logs dir of the controller.'))

        if controller_cleanup:
            logging.info('{0} Cleaning controller'.format(test_type))
            controller_utils.cleanup_controller(controller_clean_handler,
                                                controller_ssh_client)

        try:
            logging.info('{0} Tearing down any existend mininet topology.'.
                          format(test_type))
            mininet_utils.stop_mininet_topo(mininet_stop_switches_handler,
                mininet_node_ip, mininet_server_rest_port)
        except:
            pass

        try:
            logging.info(
                '{0} Killing REST daemon in Mininet VM and existing topology.'.
                format(test_type))
            mininet_utils.stop_mininet_server(mininet_ssh_client,
                                              mininet_server_rest_port)
        except:
            pass

        logging.info('{0} Delete handleres from Mininet VM'.format(test_type))
        mininet_utils.delete_mininet_handlers(mininet_node_ip, mininet_node_username,
            mininet_node_password, '/tmp/transfered_files/',
            mininet_node_ssh_port)
        mininet_ssh_client.close()


def get_report_spec(test_type, config_json, results_json):
    """It returns all the information that is needed for the generation of the
    report for the specific test.

    :param test_type: Describes the type of the specific test. This value
    defines the Title of the html report.
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
             ('controller_node_ip', 'Controller IP address'),
             ('controller_port', 'Controller listening port'),
             ('controller_rebuild', 'Controller rebuild between test repeats'),
             ('controller_logs_dir', 'Controller log save directory'),
             ('controller_restconf_port', 'Controller restconf port'),
             ('mininet_boot_handler', 'Mininet boot handler'),
             ('mininet_stop_switches_handler',
              'Mininet stop switches handler'),
             ('mininet_get_switches_handler', 'Mininet get switches handler'),
             ('mininet_init_topo_handler',
              'Mininet initialize topology handler'),
             ('mininet_start_topo_handler', 'Mininet start topology handler'),
             ('mininet_node_ip', 'Mininet IP address'),
             ('mininet_server_rest_port', 'Mininet port'),
             ('mininet_size', 'Mininet network size'),
             ('mininet_topology_type', 'Mininet topology type'),
             ('mininet_hosts_per_switch', 'Mininet hosts per switch'),
             ('java_opts', 'JVM options')], config_json)],
        [report_spec.TableSpec('2d', 'Test results',
            [('global_sample_id', 'Sample ID'),
             ('timestamp', 'Sample timestamp (seconds)'),
             ('date', 'Sample timestamp (date)'),
             ('bootup_time_secs', 'Time to discover switches (seconds)'),
             ('discovered_switches', 'Discovered switches'),
             ('mininet_size', 'Mininet Size'),
             ('mininet_topology_type', 'Mininet Topology Type'),
             ('mininet_hosts_per_switch', 'Mininet Hosts per Switch'),
             ('mininet_group_size', 'Mininet Group Size'),
             ('mininet_group_delay_ms', 'Mininet Group Delay (ms)'),
             ('controller_node_ip', 'Controller IP'),
             ('controller_port', 'Controller port'),
             ('controller_java_xopts', 'Java options'),
             ('one_minute_load', 'One minute load'),
             ('five_minute_load', 'five minutes load'),
             ('fifteen_minute_load', 'fifteen minutes load'),
             ('used_memory_bytes', 'System used memory (Bytes)'),
             ('total_memory_bytes', 'Total system memory'),
             ('controller_cpu_system_time', 'Controller CPU system time'),
             ('controller_cpu_user_time', 'Controller CPU user time'),
             ('controller_num_threads', 'Controller threads'),
             ('controller_num_fds', 'Controller num of fds'),
             ('controller_statistics_period_ms',
              'Controller Statistics Period (ms)')], results_json)])

    return report_spec_obj
