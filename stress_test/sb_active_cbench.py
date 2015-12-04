# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Active Southbound Performance test """

import cbench_utils
import collections
import common
import controller_utils
import itertools
import json
import logging
import multiprocessing
import os
import queue
import re
import report_spec
import sys
import util.file_ops
import util.netutil



def monitor(data_queue, result_queue, cpid, global_sample_id, repeat_id,
            test_repeats, cbench_switches, cbench_switches_per_thread,
            cbench_threads, cbench_delay_before_traffic_ms,
            cbench_thread_creation_delay_ms, cbench_simulated_hosts,
            cbench_ms_per_test, cbench_internal_repeats, cbench_warmup,
            cbench_mode, controller_statistics_period_ms, controller_port,
            controller_node_ip, controller_node_ssh_port,
            controller_node_username, controller_node_password, term_success,
            term_fail):
    """ Function executed by the monitor thread

    :param data_queue: data queue where monitor receives Cbench output line
    by line
    :param result_queue: result queue used by monitor to send result to main
    :param cpid: controller PID
    :param global_sample_id: unique ascending ID for the next sample
    :param repeat_id: ID of the test repeat
    :param cbench_switches: total number of simulated switches
    :param cbench_switches_per_thread: number of sim. switches per thread
    :param cbench_threads: total number of Cbench threads
    :param cbench_delay_before_traffic_ms: delay before traffic transmission
    (in milliseconds)
    :param cbench_thread_creation_delay_ms: delay between thread creation
    (in milliseconds)
    :param cbench_simulated_hosts: number of simulated hosts
    :param cbench_ms_per_test: duration (in (ms)) of Cbench internal
    iteration
    :param cbench_internal_repeats: number of internal iterations during traffic
    transmission where performance and other statistics are sampled
    :param cbench_warmup: number of initial internal iterations that were
    treated as "warmup" and  are not considered when computing aggregate
    performance results
    :param cbench_mode: (one of "Latency" or "Throughput", see Cbench
    documentation)
    :param controller_statistics_period_ms: Interval that controller sends
    statistics flow requests to the switches (in milliseconds)
    :param controller_port: controller port number where OF switches should
    connect
    :param controller_node_ip: controller node IP address
    :param controller_node_ssh_port: ssh port of controller node
    (controller_node_ip)
    :param controller_node_username: username of the controller node
    :param controller_node_password: password of the controller node
    :param term_success: The success message when we have success in Cbench thread
    :param term_fail: The fail message
    :type data_queue: multiprocessing.Queue
    :type result_queue: multiprocessing.Queue
    :type cpid: int
    :type global_sample_id: int
    :type repeat_id: int
    :type cbench_switches: int
    :type cbench_switches_per_thread: int
    :type cbench_threads: int
    :type cbench_delay_before_traffic_ms: int
    :type cbench_thread_creation_delay_ms: int
    :type cbench_simulated_hosts: int
    :type cbench_ms_per_test: int
    :type cbench_internal_repeats: int
    :type cbench_warmup: int
    :type cbench_mode: str
    :type controller_statistics_period_ms: int
    :type controller_port: str
    :type controller_node_ip: str
    :type controller_node_ssh_port: str
    :type controller_node_username: str
    :type controller_node_password: str
    """

    internal_repeat_id = 0
    logging.info('[monitor_thread] Monitor thread started')

    # will hold samples taken in the lifetime of this thread
    samples = []
        # Opening connection with mininet_node_ip and returning
        # cbench_ssh_client to be utilized in the sequel
    node_parameters = collections.namedtuple('ssh_connection',
        ['name', 'ip', 'ssh_port', 'username', 'password'])
    controller_node = node_parameters('Controller',
                                      controller_node_ip.value.decode(),
                                      int(controller_node_ssh_port.value.decode()),
                                      controller_node_username.value.decode(),
                                      controller_node_password.value.decode())

    controller_ssh_client =  common.open_ssh_connections([controller_node])[0]

    while True:
        try:
            # read messages from queue while TERM_SUCCESS has not been sent
            line = data_queue.get(block=True, timeout=10000)
            if line == term_success.value.decode():
                logging.info('[monitor_thread] successful termination '
                              'string returned. Returning samples and exiting.')
                result_queue.put(samples, block=True)
                return
            else:
                # look for lines containing a substring like e.g.
                # 'total = 1.2345 per ms'
                match = re.search(r'total = (.+) per ms', line)
                if match is not None or line == term_fail.value.decode():
                    statistics = common.sample_stats(cpid.value,
                                                     controller_ssh_client)
                    statistics['global_sample_id'] = \
                        global_sample_id.value
                    global_sample_id.value += 1
                    statistics['repeat_id'] = repeat_id.value
                    statistics['internal_repeat_id'] = internal_repeat_id
                    statistics['cbench_simulated_hosts'] = \
                        cbench_simulated_hosts.value
                    statistics['cbench_switches'] = \
                        cbench_switches.value
                    statistics['cbench_threads'] = \
                        cbench_threads.value
                    statistics['cbench_switches_per_thread'] = \
                        cbench_switches_per_thread.value
                    statistics['cbench_thread_creation_delay_ms'] = \
                        cbench_thread_creation_delay_ms.value
                    statistics['cbench_delay_before_traffic_ms'] = \
                        cbench_delay_before_traffic_ms.value
                    statistics['controller_statistics_period_ms'] = \
                        controller_statistics_period_ms.value
                    statistics['test_repeats'] = test_repeats.value
                    statistics['controller_node_ip'] = controller_node.ip
                    statistics['controller_port'] = str(controller_port.value)
                    statistics['cbench_mode'] = cbench_mode.value.decode()
                    statistics['cbench_ms_per_test'] = cbench_ms_per_test.value
                    statistics['cbench_internal_repeats'] = \
                        cbench_internal_repeats.value
                    statistics['cbench_warmup'] = cbench_warmup.value
                    if line == term_fail.value.decode():
                        logging.info(
                            '[monitor_thread] returned failed termination string.'
                            'returning gathered samples and exiting.')

                        statistics['throughput_responses_sec'] = -1
                        samples.append(statistics)
                        result_queue.put(samples, block=True)
                        return

                    if match is not None:

                        # extract the numeric portion from the above regex
                        statistics['throughput_responses_sec'] = \
                            float(match.group(1)) * 1000.0

                        samples.append(statistics)
                    internal_repeat_id += 1

        except queue.Empty as exept:
            logging.error('[monitor_thread] {0}'.format(str(exept)))


def sb_active_cbench_run(out_json, ctrl_base_dir, sb_gen_base_dir, conf,
                         output_dir):
    """Run test. This is the main function that is called from
    nstat_orchestrator and performs the specific test.

    :param out_json: the JSON output file
    :param ctrl_base_dir: controller base directory
    :param sb_gen_base_dir: Cbench base directory
    :param conf: JSON configuration dictionary
    :param output_dir: directory to store output files
    :type out_json: str
    :type ctrl_base_dir: str
    :type sb_gen_base_dir: str
    :type conf: str
    :type output_dir: str
    """

    test_type = '[sb_active_cbench]'
    logging.info('{0} initializing test parameters'.format(test_type))

    # Cbench parameters
    cbench_build_handler = sb_gen_base_dir + conf['cbench_build_handler']
    cbench_clean_handler = sb_gen_base_dir + conf['cbench_clean_handler']
    cbench_rebuild = conf['cbench_rebuild']
    cbench_cleanup = conf['cbench_cleanup']
    cbench_name = conf['cbench_name']

    cbench_run_handler  = multiprocessing.Array('c', str(sb_gen_base_dir + \
        conf['cbench_run_handler']).encode())
    controller_node_ip = multiprocessing.Array('c',
        str(conf['controller_node_ip']).encode())
    controller_port = multiprocessing.Value('i', conf['controller_port'])
    cbench_threads = multiprocessing.Value('i', 0)
    cbench_switches_per_thread = multiprocessing.Value('i', 0)
    cbench_switches = multiprocessing.Value('i', 0)
    cbench_thread_creation_delay_ms = multiprocessing.Value('i', 0)
    cbench_delay_before_traffic_ms = multiprocessing.Value('i', 0)
    cbench_ms_per_test = multiprocessing.Value('i', conf['cbench_ms_per_test'])
    cbench_internal_repeats = \
        multiprocessing.Value('i', conf['cbench_internal_repeats'])
    cbench_simulated_hosts = multiprocessing.Value('i', 0)
    cbench_warmup = multiprocessing.Value('i', conf['cbench_warmup'])
    cbench_node_ip = multiprocessing.Array('c',
        str(conf['cbench_node_ip']).encode())
    cbench_node_ssh_port = multiprocessing.Array('c',
        str(conf['cbench_node_ssh_port']).encode())
    cbench_node_username = multiprocessing.Array('c',
        str(conf['cbench_node_username']).encode())
    cbench_node_password = multiprocessing.Array('c',
        str(conf['cbench_node_password']).encode())
    cbench_mode= multiprocessing.Array('c', str(conf['cbench_mode']).encode())

    # Controller parameters
    controller_statistics_period_ms = multiprocessing.Value('i', 0)
    controller_build_handler = ctrl_base_dir + conf['controller_build_handler']
    controller_start_handler = ctrl_base_dir + conf['controller_start_handler']
    controller_status_handler = \
        ctrl_base_dir + conf['controller_status_handler']
    controller_stop_handler = ctrl_base_dir + conf['controller_stop_handler']
    controller_clean_handler = ctrl_base_dir + conf['controller_clean_handler']
    controller_statistics_handler = \
        ctrl_base_dir + conf['controller_statistics_handler']
    controller_logs_dir = ctrl_base_dir + conf['controller_logs_dir']
    controller_node_ssh_port = multiprocessing.Array('c',
        str(conf['controller_node_ssh_port']).encode())
    controller_node_username = multiprocessing.Array('c',
        str(conf['controller_node_username']).encode())
    controller_node_password = multiprocessing.Array('c',
        str(conf['controller_node_password']).encode())
    controller_rebuild = conf['controller_rebuild']
    controller_cleanup = conf['controller_cleanup']

    # Shared read-write variables between monitor-main thread and
    # Cbench thread.
    repeat_id = multiprocessing.Value('i', 0)
    cpid = multiprocessing.Value('i', 0)
    global_sample_id = multiprocessing.Value('i', 0)
    test_repeats = multiprocessing.Value('i', conf['test_repeats'])
    java_opts = conf['java_opts']

    node_parameters = collections.namedtuple('ssh_connection',
        ['name', 'ip', 'ssh_port', 'username', 'password'])
    controller_handlers = collections.namedtuple('controller_handlers',
        ['ctrl_build_handler','ctrl_start_handler','ctrl_status_handler',
         'ctrl_stop_handler', 'ctrl_clean_handler'])
    cbench_handlers = collections.namedtuple('cbench_handlers' ,
        ['cbench_build_handler','cbench_clean_handler',
         'cbench_run_handler'])
    controller_node = node_parameters('Controller',
                                      controller_node_ip.value.decode(),
                                      int(controller_node_ssh_port.value.decode()),
                                      controller_node_username.value.decode(),
                                      controller_node_password.value.decode())
    cbench_node = node_parameters('MT-Cbench', cbench_node_ip.value.decode(),
                                   int(cbench_node_ssh_port.value.decode()),
                                   cbench_node_username.value.decode(),
                                   cbench_node_password.value.decode())
    controller_handlers_set = controller_handlers(controller_build_handler,
        controller_start_handler, controller_status_handler,
        controller_stop_handler, controller_clean_handler)
    cbench_handlers_set = cbench_handlers(cbench_build_handler,
        cbench_clean_handler, cbench_run_handler.value.decode())

    # termination message sent to monitor thread when Cbench is finished
    term_success = multiprocessing.Array('c',
        str('__successful_termination__').encode())
    term_fail = multiprocessing.Array('c',
        str('__failed_termination__').encode())

    # list of samples: each sample is a dictionary that contains all
    # information that describes a single measurement, i.e.:
    #    - the actual performance results
    #    - secondary runtime statistics
    #    - current values of test dimensions (dynamic)
    #    - test configuration options (static)
    total_samples = []

    try:

        # Before proceeding with the experiments check validity of all
        # handlers

        logging.info('{0} checking handler files.'.format(test_type))
        util.file_ops.check_filelist([controller_build_handler,
            controller_start_handler, controller_status_handler,
            controller_stop_handler, controller_clean_handler,
            controller_statistics_handler, cbench_build_handler,
            cbench_run_handler.value.decode(), cbench_clean_handler])

        # Opening connection with mininet_node_ip and returning
        # cbench_ssh_client to be utilized in the sequel
        cbench_ssh_client, controller_ssh_client = \
            common.open_ssh_connections([cbench_node, controller_node])

        if cbench_rebuild:
            logging.info('{0} building cbench.'.format(test_type))
            cbench_utils.rebuild_cbench(cbench_build_handler, cbench_ssh_client)

        # Controller common actions: rebuild controller if controller_rebuild is
        # SET, check_for_active controller, generate_controller_xml_files
        controller_utils.controller_pre_actions(controller_handlers_set,
                                      controller_rebuild, controller_ssh_client,
                                      java_opts, controller_port.value)

        # run tests for all possible dimensions
        for (cbench_threads.value,
             cbench_switches_per_thread.value,
             cbench_thread_creation_delay_ms.value,
             cbench_delay_before_traffic_ms.value,
             cbench_simulated_hosts.value,
             repeat_id.value,
             controller_statistics_period_ms.value) in \
             itertools.product(conf['cbench_threads'],
                               conf['cbench_switches_per_thread'],
                               conf['cbench_thread_creation_delay_ms'],
                               conf['cbench_delay_before_traffic_ms'],
                               conf['cbench_simulated_hosts'],
                               list(range(0, test_repeats.value)),
                               conf['controller_statistics_period_ms']):

            logging.info('{0} changing controller statistics period to {1} ms'.
                format(test_type, controller_statistics_period_ms.value))
            controller_utils.controller_changestatsperiod(
                controller_statistics_handler,
                controller_statistics_period_ms.value, controller_ssh_client)

            logging.info('{0} starting controller'.format(test_type))
            cpid.value = controller_utils.start_controller(
                controller_start_handler, controller_status_handler,
                controller_port.value, ' '.join(conf['java_opts']),
                controller_ssh_client)
            logging.info('{0} OK, controller status is 1.'.format(test_type))

            cbench_switches.value = \
                cbench_threads.value * cbench_switches_per_thread.value

            logging.info('{0} creating data and result queues'.
                          format(test_type))
            data_queue = multiprocessing.Queue()
            result_queue = multiprocessing.Queue()

            logging.info('{0} creating monitor thread'.format(test_type))
            monitor_thread = multiprocessing.Process(
                target=monitor, args=(data_queue, result_queue,
                                      cpid, global_sample_id, repeat_id,
                                      test_repeats,
                                      cbench_switches,
                                      cbench_switches_per_thread,
                                      cbench_threads,
                                      cbench_delay_before_traffic_ms,
                                      cbench_thread_creation_delay_ms,
                                      cbench_simulated_hosts,
                                      cbench_ms_per_test,
                                      cbench_internal_repeats,
                                      cbench_warmup, cbench_mode,
                                      controller_statistics_period_ms,
                                      controller_port,
                                      controller_node_ip,
                                      controller_node_ssh_port,
                                      controller_node_username,
                                      controller_node_password,
                                      term_success, term_fail))

            logging.info('{0} creating cbench thread'.format(test_type))
            cbench_thread = multiprocessing.Process(
                target=cbench_utils.cbench_thread,
                args=(cbench_run_handler, controller_node_ip,
                      controller_port, cbench_threads,
                      cbench_switches_per_thread,
                      cbench_switches,
                      cbench_thread_creation_delay_ms,
                      cbench_delay_before_traffic_ms,
                      cbench_ms_per_test, cbench_internal_repeats,
                      cbench_simulated_hosts, cbench_warmup,
                      cbench_mode,
                      cbench_node_ip,
                      cbench_node_ssh_port,
                      cbench_node_username,
                      cbench_node_password, term_success, term_fail,
                      data_queue))

            # Parallel section: starting monitor/cbench threads
            monitor_thread.start()
            cbench_thread.start()

            samples = result_queue.get(block=True)
            total_samples = total_samples + samples
            logging.info('{0} joining monitor thread'.format(test_type))
            monitor_thread.join()
            logging.info('{0} joining cbench thread'.format(test_type))
            cbench_thread.join()

            controller_utils.stop_controller(controller_stop_handler,
                controller_status_handler, cpid.value, controller_ssh_client)

    except:
        logging.error('{0} :::::::::: Exception caught :::::::::::'.
                      format(test_type))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error('{0} Exception: {1}, {2}'.
                      format(test_type, exc_type, exc_tb.tb_lineno))

        errors = str(exc_obj).rstrip().split('\n')
        for error in errors:
            logging.error('{0} {1}'.format(test_type, error))
        logging.exception('')

    finally:
        logging.info('{0} finalizing test'.format(test_type))

        logging.info('{0} creating test output directory if not present.'.
                     format(test_type))
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        logging.info('{0} saving results to JSON file.'.format(test_type))
        common.generate_json_results(total_samples, out_json)

        try:
            logging.info('{0} stopping controller.'.
                         format(test_type))
            controller_utils.stop_controller(controller_stop_handler,
                controller_status_handler, cpid.value, controller_ssh_client)
        except:
            pass

        try:
            logging.info('{0} collecting logs'.format(test_type))
            util.netutil.copy_remote_directory(controller_node,
                controller_logs_dir, output_dir + '/log')
        except:
            logging.error('{0} {1}'.format(
                test_type, 'failed transferring controller logs directory.'))

        if controller_cleanup:
            logging.info('{0} cleaning controller build directory.'.format(test_type))
            controller_utils.cleanup_controller(controller_clean_handler,
                                                controller_ssh_client)

        if cbench_cleanup:
            logging.info('{0} cleaning cbench build directory.'.format(test_type))
            cbench_utils.cleanup_cbench(cbench_clean_handler, cbench_ssh_client)

        # Closing ssh connections with controller/cbench nodes
        if controller_ssh_client:
            controller_ssh_client.close()
        else:
            logging.error('{0} controller ssh connection does not exist.'.
                          format(test_type))
        if cbench_ssh_client:
            cbench_ssh_client.close()
        else:
            logging.error('{0} cbench ssh connection does not exist.'.
                          format(test_type))

def get_report_spec(test_type, config_json, results_json):
    """It returns all the information that is needed for the generation of the
    report for the specific test.

    :param test_type: describes the type of the specific test. This value
    defines the title of the html report.
    :param config_json: This is the filepath to the configuration json file.
    :param results_json: This is the filepath to the results json file.
    :returns: A ReportSpec object that holds all the test report information
    and is passed as input to the generate_html() function in the
    html_generation.py, that is responsible for the report generation.
    :rtype: ReportSpec
    :type: test_type: str
    :type: config_json: str
    :type: results_json: str
    """

    report_spec_obj = report_spec.ReportSpec(
        config_json, results_json, '{0}'.format(test_type),
        [report_spec.TableSpec(
            '1d', 'Test configuration parameters (detailed)',
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
             ('controller_port', 'Controller Southbound port'),
             ('controller_rebuild', 'Controller rebuild between test repeats'),
             ('controller_logs_dir', 'Controller log save directory'),
             ('cbench_name', 'Generator name'),
             ('cbench_node_ip', 'Cbench node IP address'),
             ('cbench_node_ssh_port', 'Cbench node ssh port'),
             ('cbench_node_username', 'Cbench node username'),
             ('cbench_node_password', 'Cbench node password'),
             ('cbench_build_handler', 'Generator build script'),
             ('cbench_run_handler', 'Generator start script'),
             ('cbench_clean_handler', 'Generator cleanup script'),
             ('cbench_simulated_hosts', 'Generator simulated hosts'),
             ('cbench_threads', 'Generator threads'),
             ('cbench_thread_creation_delay_ms',
              'Generation delay in ms between thread creation'),
             ('cbench_switches_per_thread',
              'Switches per generator thread'),
             ('cbench_internal_repeats', 'Generator internal repeats'),
             ('cbench_ms_per_test', 'Internal repeats duration in ms'),
             ('cbench_rebuild',
              'Generator rebuild between each test repeat'),
             ('cbench_mode', 'Generator testing mode'),
             ('cbench_warmup', 'Generator warmup repeats'),
             ('cbench_delay_before_traffic_ms',
              'Generator delay before sending traffic in ms'),
             ('java_opts', 'JVM options')
            ], config_json)],
        [report_spec.TableSpec('2d', 'Test results',
            [('global_sample_id', 'Sample ID'),
             ('timestamp', 'Sample timestamp (seconds)'),
             ('date', 'Sample timestamp (date)'),
             ('test_repeats', 'Total test repeats'),
             ('repeat_id', 'External repeat ID'),
             ('cbench_internal_repeats', 'Generator Internal repeats'),
             ('internal_repeat_id', 'Internal repeat ID'),
             ('throughput_responses_sec', 'Throughput (responses/sec)'),
             ('cbench_simulated_hosts', 'Generator simulated hosts'),
             ('cbench_switches', 'Generated simulated switches'),
             ('cbench_threads', 'Generator threads'),
             ('cbench_switches_per_thread',
              'Switches per generator thread'),
             ('cbench_thread_creation_delay_ms',
              'Generator delay before traffic transmission (ms)'),
             ('cbench_delay_before_traffic_ms',
              'Delay between switches requests (ms)'),
             ('cbench_ms_per_test', 'Internal repeats interval'),
             ('cbench_warmup', 'Generator warmup repeats'),
             ('cbench_mode', 'Generator test mode'),
             ('controller_node_ip', 'Controller IP node address'),
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
              'Controller statistics period (ms)')
            ], results_json)])
    return report_spec_obj
