# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Idle Southbound Performance test """

import common
import controller_utils
import generator_utils
import itertools
import json
import logging
import multiprocessing
import os
import report_spec
import shutil
import sys
import util.file_ops


def sb_idle_cbench_run(out_json, ctrl_base_dir, sb_gen_base_dir,
                       conf, output_dir):
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

    # Global variables read-write shared between monitor-main thread.
    cpid = 0
    global_sample_id = 0
    test_type = '[sb_idle_cbench]'

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
    controller_restconf_port = conf['controller_restconf_port']
    controller_restconf_auth_token = (conf['controller_restconf_user'],
                                      conf['controller_restconf_password'])
    controller_logs_dir = ctrl_base_dir + conf['controller_logs_dir']
    controller_rebuild = conf['controller_rebuild']
    controller_cpu_shares = conf['controller_cpu_shares']
    controller_cleanup = conf['controller_cleanup']

    generator_build_handler = sb_gen_base_dir + conf['generator_build_handler']
    generator_run_handler = sb_gen_base_dir + conf['generator_run_handler']
    generator_clean_handler = sb_gen_base_dir + conf['generator_clean_handler']
    generator_rebuild = conf['generator_rebuild']
    generator_cleanup = conf['generator_cleanup']
    generator_name = conf['generator_name']
    generator_simulated_hosts = conf['generator_simulated_hosts']
    generator_delay_before_traffic_ms = \
        conf['generator_delay_before_traffic_ms']
    generator_mode = conf['generator_mode']
    generator_warmup = conf['generator_warmup']
    generator_ms_per_test = conf['generator_ms_per_test']
    generator_internal_repeats = conf['generator_internal_repeats']
    generator_cpu_shares = conf['generator_cpu_shares']
    generator_rebuild = conf['generator_rebuild']

    # list of samples: each sample is a dictionary that contains all
    # information that describes a single measurement, i.e.:
    #    - the actual performance results
    #    - secondary runtime statistics
    #    - current values of test dimensions (dynamic)
    #    - test configuration options (static)
    total_samples = []

    try:
        controller_cpus_str, generator_cpus_str = \
            common.create_cpu_shares(controller_cpu_shares,
                                     generator_cpu_shares)
        # Before proceeding with the experiments check validity of all
        # handlers
        util.file_ops.check_filelist([controller_build_handler,
            controller_start_handler, controller_status_handler,
            controller_stop_handler, controller_clean_handler,
            controller_statistics_handler, generator_build_handler,
            generator_run_handler, generator_clean_handler])

        if generator_rebuild:
            logging.info('{0} Building generator.'.format(test_type))
            generator_utils.rebuild_generator(generator_build_handler)

        if controller_rebuild:
            logging.info('{0} Building controller.'.format(test_type))
            controller_utils.rebuild_controller(controller_build_handler)

        controller_utils.check_for_active_controller(controller_port)

        os.environ['JAVA_OPTS'] = ' '.join(conf['java_opts'])

        logging.info('{0} Starting and stopping controller to '
                     'generate xml files'.format(test_type))
        cpid = controller_utils.start_controller(controller_start_handler,
            controller_status_handler, controller_port, controller_cpus_str)
        # Controller status check is done inside start_controller() of the
        # controller_utils
        logging.info('{0} OK, controller status is 1.'.format(test_type))
        controller_utils.stop_controller(controller_stop_handler,
            controller_status_handler, cpid)

        # Run tests for all possible dimensions
        for (generator_threads,
             generator_switches_per_thread,
             generator_thread_creation_delay_ms,
             controller_statistics_period_ms) in \
             itertools.product(conf['generator_threads'],
                               conf['generator_switches_per_thread'],
                               conf['generator_thread_creation_delay_ms'],
                               conf['controller_statistics_period_ms']):

            controller_utils.controller_changestatsperiod(
                controller_statistics_handler,
                controller_statistics_period_ms)

            logging.info('{0} Starting controller'.format(test_type))
            cpid = controller_utils.start_controller(controller_start_handler,
                controller_status_handler, controller_port,
                controller_cpus_str)
            logging.info('{0} OK, controller status is 1.'.format(test_type))
            generator_switches = \
                generator_threads * generator_switches_per_thread

            logging.debug('{0} Creating queue'.format(test_type))
            result_queue = multiprocessing.Queue()

            sleep_ms = \
                generator_threads * generator_thread_creation_delay_ms
            total_cbench_switches = \
                generator_threads * generator_switches_per_thread
            total_cbench_hosts = \
                generator_simulated_hosts * total_cbench_switches
            # We want this value to be big, equivalent to the topology size.
            discovery_deadline_ms = \
                (7000 * (total_cbench_switches + total_cbench_hosts)) + sleep_ms
            logging.debug('{0} Creating monitor thread'.format(test_type))
            monitor_thread = multiprocessing.Process(
                target=common.poll_ds_thread,
                args=(controller_ip, controller_restconf_port,
                      controller_restconf_auth_token, sleep_ms,
                      generator_switches, discovery_deadline_ms, result_queue))

            logging.debug('{0} Creating generator thread'.format(test_type))
            generator_thread = multiprocessing.Process(
                target=generator_utils.generator_thread,
                args=(generator_run_handler, generator_cpus_str, controller_ip,
                      controller_port, generator_threads,
                      generator_switches_per_thread, generator_switches,
                      generator_thread_creation_delay_ms,
                      generator_delay_before_traffic_ms,
                      generator_ms_per_test,
                      conf['generator_internal_repeats'],
                      conf['generator_simulated_hosts'],
                      conf['generator_warmup'], conf['generator_mode']))

            # Parallel section
            monitor_thread.start()
            generator_thread.start()
            res = result_queue.get(block=True)
            logging.debug('{0} Joining monitor thread'.format(test_type))
            monitor_thread.join()
            # After the monitor thread joins, we no longer need the generator
            # because the actual test has been completed and we have the
            # results. That is why we do not wait generator thread to return
            # and we stop it with a termination signal.
            logging.debug('{0} Terminating generator thread'.format(test_type))
            generator_thread.terminate()
            # It is important to join() the process after terminating it in
            # order to give the background machinery time to update the status
            # of the object to reflect the termination.
            generator_thread.join()

            statistics = common.sample_stats(cpid)
            statistics['global_sample_id'] = global_sample_id
            global_sample_id += 1
            statistics['generator_simulated_hosts'] = \
                conf['generator_simulated_hosts']
            statistics['generator_switches'] = generator_switches
            statistics['generator_threads'] = generator_threads
            statistics['generator_switches_per_thread'] = \
                generator_switches_per_thread
            statistics['generator_thread_creation_delay_ms'] = \
                generator_thread_creation_delay_ms
            statistics['controller_cpu_shares'] = \
                '{0}%'.format(controller_cpu_shares)
            statistics['controller_statistics_period_ms'] = \
                controller_statistics_period_ms
            statistics['generator_delay_before_traffic_ms'] = \
                conf['generator_delay_before_traffic_ms']
            statistics['controller_ip'] = controller_ip
            statistics['controller_port'] = str(controller_port)
            statistics['generator_mode'] = generator_mode
            statistics['generator_ms_per_test'] = generator_ms_per_test
            statistics['generator_internal_repeats'] = \
                generator_internal_repeats
            statistics['generator_cpu_shares'] = \
                '{0}%'.format(generator_cpu_shares)
            statistics['generator_warmup'] = generator_warmup
            statistics['bootup_time_secs'] = res[1]
            statistics['discovered_switches'] = res[2]
            generator_thread.terminate()
            total_samples.append(statistics)

            controller_utils.stop_controller(controller_stop_handler,
                controller_status_handler, cpid)

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
        logging.info('{0} Finalizing test')

        logging.info('{0} Creating test output dirctory if not exist.'.
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
            generator_utils.cleanup_generator(generator_clean_handler)


def get_report_spec(test_type, config_json, results_json):
    """It returns all the information that is needed for the generation of the
    report for the specific test.

    :param test_type: describes the type of the specific test. This value
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
            [('controller_name', 'Controller name'),
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
             ('generator_warmup','Generator warmup repeats'),
             ('generator_delay_before_traffic_ms',
              'Generator delay before sending traffic in ms'),
             ('java_opts', 'JVM options')], config_json)],
        [report_spec.TableSpec('2d', 'Test results',
            [('global_sample_id', 'Sample ID'),
             ('timestamp', 'Sample timestamp (seconds)'),
             ('date', 'Sample timestamp (date)'),
             ('generator_internal_repeats', 'Generator Internal repeats'),
             ('bootup_time_secs', 'Time to discover switches (seconds)'),
             ('discovered_switches', 'Discovered switches'),
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
             ('generator_cpu_shares', 'Generator CPU percentage'),
             ('controller_ip', 'Controller IP'),
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
              'Controller statistics period (ms)')], results_json)])

    return report_spec_obj
