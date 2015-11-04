# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Active Southbound Performance test """

import controller_utils
import common
import cbench_utils
import itertools
import json
import logging
import multiprocessing
import os
import queue
import re
import report_spec
import shutil
import sys
import util.file_ops



# termination message sent to monitor thread when generator is finished
TERM_SUCCESS = '__successful_termination__'
TERM_FAIL = '__failed_termination__'


def monitor(data_queue, result_queue, conf, cpid, global_sample_id, repeat_id,
            generator_switches, generator_switches_per_thread,
            generator_threads, generator_delay_before_traffic_ms,
            generator_thread_creation_delay_ms, generator_simulated_hosts,
            controller_statistics_period_ms):
    """ Function executed by the monitor thread

    :param data_queue: data queue where monitor receives generator output line
    by line
    :param result_queue: result queue used by monitor to send result to main
    :param conf: test configuration
    :param cpid: controller PID
    :param global_sample_id: unique ascending ID for the next sample
    :param repeat_id: ID of the test repeat
    :param generator_switches: total number of simulated switches
    :param generator_switches_per_thread: number of sim. switches per thread
    :param generator_threads: total number of generator threads
    :param generator_delay_before_traffic_ms: delay before traffic transmission
    (in milliseconds)
    :param generator_thread_creation_delay_ms: delay between thread creation
    (in milliseconds)
    :param generator_simulated_hosts: number of simulated hosts
    :param controller_statistics_period_ms: Interval that controller sends
    statistics flow requests to the switches (in milliseconds)
    :type data_queue: multiprocessing.Queue
    :type result_queue: multiprocessing.Queue
    :type conf: dict
    :type cpid: int
    :type global_sample_id: int
    :type repeat_id: int
    :type generator_switches: int
    :type generator_switches_per_thread: int
    :type generator_threads: int
    :type generator_delay_before_traffic_ms: int
    :type generator_thread_creation_delay_ms: int
    :type generator_simulated_hosts: int
    :type controller_statistics_period_ms: int
    """

    internal_repeat_id = 0
    logging.debug('[monitor_thread] Monitor thread started')
    # will hold samples taken in the lifetime of this thread
    samples = []

    while True:
        try:
            # read messages from queue while TERM_SUCCESS has not been sent
            line = data_queue.get(block=True, timeout=10000)
            if line == TERM_SUCCESS:
                logging.debug('[monitor_thread] Got successful termination '
                              'string. Returning samples and exiting.')
                result_queue.put(samples, block=True)
                return
            else:
                # look for lines containing a substring like e.g.
                # 'total = 1.2345 per ms'
                match = re.search(r'total = (.+) per ms', line)
                if match is not None or line == TERM_FAIL:
                    statistics = common.sample_stats(cpid.value)
                    statistics['global_sample_id'] = \
                        global_sample_id.value
                    global_sample_id.value += 1
                    statistics['repeat_id'] = repeat_id.value
                    statistics['internal_repeat_id'] = internal_repeat_id
                    statistics['generator_simulated_hosts'] = \
                        generator_simulated_hosts.value
                    statistics['generator_switches'] = \
                        generator_switches.value
                    statistics['generator_threads'] = \
                        generator_threads.value
                    statistics['generator_switches_per_thread'] = \
                        generator_switches_per_thread.value
                    statistics['generator_thread_creation_delay_ms'] = \
                        generator_thread_creation_delay_ms.value
                    statistics['generator_delay_before_traffic_ms'] = \
                        generator_delay_before_traffic_ms.value

                    statistics['controller_statistics_period_ms'] = \
                        controller_statistics_period_ms.value
                    statistics['test_repeats'] = conf['test_repeats']
                    statistics['controller_ip'] = conf['controller_ip']
                    statistics['controller_port'] = \
                        str(conf['controller_port'])

                    statistics['generator_mode'] = conf['generator_mode']
                    statistics['generator_ms_per_test'] = \
                        conf['generator_ms_per_test']
                    statistics['generator_internal_repeats'] = \
                        conf['generator_internal_repeats']
                    statistics['generator_warmup'] = \
                        conf['generator_warmup']
                    if line == TERM_FAIL:
                        logging.debug(
                            '[monitor_thread] Got failed termination string.'
                            'Returning samples gathered so far and exiting.')

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
    :param sb_gen_base_dir: generator base directory
    :param conf: JSON configuration dictionary
    :param output_dir: directory to store output files
    :type out_json: str
    :type ctrl_base_dir: str
    :type sb_gen_base_dir: str
    :type conf: str
    :type output_dir: str
    """

    # Shared read-write variables between monitor-main thread and
    # generator thread.
    repeat_id = multiprocessing.Value('i', 0)
    cpid = multiprocessing.Value('i', 0)
    generator_threads = multiprocessing.Value('i', 0)
    generator_switches_per_thread = multiprocessing.Value('i', 0)
    generator_thread_creation_delay_ms = multiprocessing.Value('i', 0)
    generator_delay_before_traffic_ms = multiprocessing.Value('i', 0)
    generator_simulated_hosts = multiprocessing.Value('i', 0)
    generator_switches = multiprocessing.Value('i', 0)
    global_sample_id = multiprocessing.Value('i', 0)
    controller_statistics_period_ms = multiprocessing.Value('i', 0)

    test_type = '[sb_active_cbench]'

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
    controller_ip = conf['controller_ip']
    controller_port = conf['controller_port']
    controller_logs_dir = ctrl_base_dir + conf['controller_logs_dir']
    controller_rebuild = conf['controller_rebuild']

    controller_cleanup = conf['controller_cleanup']

    generator_build_handler = sb_gen_base_dir + conf['generator_build_handler']
    generator_run_handler = sb_gen_base_dir + conf['generator_run_handler']
    generator_clean_handler = sb_gen_base_dir + conf['generator_clean_handler']
    generator_rebuild = conf['generator_rebuild']
    generator_cleanup = conf['generator_cleanup']
    generator_name = conf['generator_name']
    generator_mode = conf['generator_mode']
    generator_warmup = conf['generator_warmup']
    generator_ms_per_test = conf['generator_ms_per_test']
    generator_internal_repeats = conf['generator_internal_repeats']

    generator_rebuild = conf['generator_rebuild']

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
        util.file_ops.check_filelist([controller_build_handler,
            controller_start_handler, controller_status_handler,
            controller_stop_handler, controller_clean_handler,
            controller_statistics_handler, generator_build_handler,
            generator_run_handler, generator_clean_handler])

        if generator_rebuild:
            logging.info('{0} Building generator.'.format(test_type))
            cbench_utils.rebuild_generator(generator_build_handler)

        if controller_rebuild:
            logging.info('{0} Building controller.'.format(test_type))
            controller_utils.rebuild_controller(controller_build_handler)

        controller_utils.check_for_active_controller(controller_port)

        os.environ['JAVA_OPTS'] = ' '.join(conf['java_opts'])

        logging.info(
            '{0} Starting and stopping controller to generate xml files'.
            format(test_type))
        cpid.value = controller_utils.start_controller(
            controller_start_handler, controller_status_handler,
            controller_port)
        # Controller status check is done inside start_controller() of the
        # controller_utils
        logging.info('{0} OK, controller status is 1.'.format(test_type))
        controller_utils.stop_controller(controller_stop_handler,
            controller_status_handler, cpid.value)

        # run tests for all possible dimensions
        for (generator_threads.value,
             generator_switches_per_thread.value,
             generator_thread_creation_delay_ms.value,
             generator_delay_before_traffic_ms.value,
             generator_simulated_hosts.value,
             repeat_id.value,
             controller_statistics_period_ms.value) in \
             itertools.product(conf['generator_threads'],
                               conf['generator_switches_per_thread'],
                               conf['generator_thread_creation_delay_ms'],
                               conf['generator_delay_before_traffic_ms'],
                               conf['generator_simulated_hosts'],
                               list(range(0, conf['test_repeats'])),
                               conf['controller_statistics_period_ms']):

            controller_utils.controller_changestatsperiod(
                controller_statistics_handler,
                controller_statistics_period_ms.value)

            logging.info('{0} Starting controller'.format(test_type))
            cpid.value = controller_utils.start_controller(
                controller_start_handler, controller_status_handler,
                controller_port)
            logging.info('{0} OK, controller status is 1.'.format(test_type))

            generator_switches.value = \
                generator_threads.value * generator_switches_per_thread.value

            logging.info('{0} Creating data and control queues'.
                          format(test_type))
            data_queue = multiprocessing.Queue()
            result_queue = multiprocessing.Queue()

            logging.info('{0} Creating monitor thread'.format(test_type))
            monitor_thread = multiprocessing.Process(
                target=monitor, args=(data_queue, result_queue, conf,
                                      cpid, global_sample_id, repeat_id,
                                      generator_switches,
                                      generator_switches_per_thread,
                                      generator_threads,
                                      generator_delay_before_traffic_ms,
                                      generator_thread_creation_delay_ms,
                                      generator_simulated_hosts,
                                      controller_statistics_period_ms))

            logging.info('{0} Creating generator thread'.format(test_type))
            generator_thread = multiprocessing.Process(
                target=cbench_utils.generator_thread,
                args=(generator_run_handler, controller_ip,
                      controller_port, generator_threads.value,
                      generator_switches_per_thread.value,
                      generator_switches.value,
                      generator_thread_creation_delay_ms.value,
                      generator_delay_before_traffic_ms.value,
                      generator_ms_per_test, generator_internal_repeats,
                      generator_simulated_hosts.value, generator_warmup,
                      generator_mode, data_queue, TERM_SUCCESS, TERM_FAIL))

            # Parallel section
            monitor_thread.start()
            generator_thread.start()
            samples = result_queue.get(block=True)
            total_samples = total_samples + samples
            logging.info('{0} Joining monitor thread'.format(test_type))
            monitor_thread.join()
            logging.info('{0} Joining generator thread'.format(test_type))
            generator_thread.join()

            controller_utils.stop_controller(controller_stop_handler,
                controller_status_handler, cpid.value)

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
                controller_status_handler, cpid)
        except:
            pass

        if os.path.isdir(controller_logs_dir):
            logging.info('{0} Collecting logs'.format(test_type))
            shutil.copytree(controller_logs_dir, output_dir+'/log')
            shutil.rmtree(controller_logs_dir)

        if controller_cleanup:
            logging.info('{0} Cleaning controller.'.format(test_type))
            controller_utils.cleanup_controller(controller_clean_handler)

        if generator_cleanup:
            logging.info('{0} Cleaning generator.'.format(test_type))
            cbench_utils.cleanup_generator(generator_clean_handler)


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
             ('controller_ip', 'Controller IP address'),
             ('controller_port', 'Controller listening port'),
             ('controller_rebuild', 'Controller rebuild between test repeats'),
             ('controller_logs_dir', 'Controller log save directory'),
             ('generator_name', 'Generator name'),
             ('generator_build_handler', 'Generator build script'),
             ('generator_run_handler', 'Generator start script'),
             ('generator_clean_handler', 'Generator cleanup script'),
             ('generator_simulated_hosts', 'Generator simulated hosts'),
             ('generator_threads', 'Generator threads'),
             ('generator_thread_creation_delay_ms',
              'Generation delay in ms between thread creation'),
             ('generator_switches_per_thread',
              'Switches per generator thread'),
             ('generator_internal_repeats', 'Generator internal repeats'),
             ('generator_ms_per_test', 'Internal repeats duration in ms'),
             ('generator_rebuild',
              'Generator rebuild between each test repeat'),
             ('generator_mode', 'Generator testing mode'),
             ('generator_warmup', 'Generator warmup repeats'),
             ('generator_delay_before_traffic_ms',
              'Generator delay before sending traffic in ms'),
             ('java_opts', 'JVM options')
            ], config_json)],
        [report_spec.TableSpec('2d', 'Test results',
            [('global_sample_id', 'Sample ID'),
             ('timestamp', 'Sample timestamp (seconds)'),
             ('date', 'Sample timestamp (date)'),
             ('test_repeats', 'Total test repeats'),
             ('repeat_id', 'External repeat ID'),
             ('generator_internal_repeats', 'Generator Internal repeats'),
             ('internal_repeat_id', 'Internal repeat ID'),
             ('throughput_responses_sec', 'Throughput (responses/sec)'),
             ('generator_simulated_hosts', 'Generator simulated hosts'),
             ('generator_switches', 'Generated simulated switches'),
             ('generator_threads', 'Generator threads'),
             ('generator_switches_per_thread',
              'Switches per generator thread'),
             ('generator_thread_creation_delay_ms',
              'Generator delay before traffic transmission (ms)'),
             ('generator_delay_before_traffic_ms',
              'Delay between switches requests (ms)'),
             ('generator_ms_per_test', 'Internal repeats interval'),
             ('generator_warmup', 'Generator warmup repeats'),
             ('generator_mode', 'Generator test mode'),
             ('controller_ip', 'Controller IP'),
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
