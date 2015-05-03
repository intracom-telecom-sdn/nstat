# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Active Southbound Performance test """

import common
import itertools
import json
import logging
import multiprocessing as mp
import Queue
import os
import re
import shutil
import sys
import subprocess as sp
import util.customsubprocess as cp
import util.process
import util.cpu
import util.file

# termination message sent to monitor thread when generator is finished
_term_success = '__successful_termination__'
_term_fail = '__failed_termination__'

def monitor(dq, rq, conf, cpid, global_sample_id, repeat_id,
            generator_switches, generator_switches_per_thread,
            generator_threads, generator_delay_before_traffic_ms,
            generator_thread_creation_delay_ms, generator_simulated_hosts):
    """ Function executed by the monitor thread

    :param dq: data queue where monitor receives generator output line by line
    :param rq: result queue used by monitor to send result to main
    :param conf: test configuration
    :param cpid: controller PID
    :param global_sample_id: unique ascending ID for the next sample
    :param repeat_id: ID of the test repeat
    :param generator_switches: total number of simulated switches
    :param generator_switches_per_thread: number of sim. switches per thread
    :param generator_threads: total number of generator threads
    :param generator_delay_before_traffic_ms: delay before traffic transmission
    :param generator_thread_creation_delay_ms: delay between thread creation
    :param generator_simulated_hosts: number of simulated hosts
    """
    internal_repeat_id = 0

    logging.debug('[monitor_thread] Monitor thread started')

    # will hold samples taken in the lifetime of this thread
    samples = []

    while True:
        try:
            # read messages from queue while _term_success has not been sent
            line = dq.get(block=True, timeout=10000)
            if line == _term_success:
                logging.debug((
                    '[monitor_thread] Got successful termination string.'
                    'Returning samples and exiting.'))
                rq.put(samples, block=True)
                return
            else:
                # look for lines containing a substring like e.g.
                # 'total = 1.2345 per ms'
                match = re.search(r'total = (.+) per ms', line)

                if match is not None or line == _term_fail:
                    s = common.sample_stats(cpid.value)
                    s['global_sample_id'] = global_sample_id.value
                    global_sample_id.value += 1
                    s['repeat_id'] = repeat_id.value
                    s['internal_repeat_id'] = internal_repeat_id
                    s['generator_simulated_hosts'] = generator_simulated_hosts.value
                    s['generator_switches'] = generator_switches.value
                    s['generator_threads'] = generator_threads.value
                    s['generator_switches_per_thread'] = generator_switches_per_thread.value
                    s['generator_thread_creation_delay_ms'] = generator_thread_creation_delay_ms.value
                    s['generator_delay_before_traffic_ms'] = generator_delay_before_traffic_ms.value
                    s['test_repeats'] = conf['test_repeats']
                    s['controller_ip'] = conf['controller_ip']
                    s['controller_port'] = str(conf['controller_port'])
                    s['generator_mode'] = conf['generator_mode']
                    s['generator_ms_per_test'] = conf['generator_ms_per_test']
                    s['generator_internal_repeats'] = conf['generator_internal_repeats']
                    s['controller_restart'] = conf['controller_restart']
                    s['generator_warmup'] = conf['generator_warmup']

                    if line == _term_fail:
                        logging.debug((
                            '[monitor_thread] Got failed termination string.'
                            'Returning samples gathered so far and exiting.'))
                        s['throughput_responses_sec'] = -1
                        samples.append(s)
                        rq.put(samples, block=True)
                        return

                    if match is not None:
                        # extract the numeric portion from the above regex
                        s['throughput_responses_sec'] = float(match.group(1))*1000.0
                        samples.append(s)
                    internal_repeat_id += 1

        except Queue.Empty as e:
            logging.error('[monitor_thread] ' + str(e))


def active_test_run(out_json, ctrl_base_dir, gen_base_dir, conf, output_dir):
    """
    Run test
    :param out_json: the JSON output file
    :param ctrl_base_dir: Test base directory
    :param gen_base_dir: Test base directory
    :param conf: JSON configuration dictionary
    :param output_dir: directory to store output files
    """

    # Global variables read-write shared between monitor-main thread.
    repeat_id = mp.Value('i', 0)
    cpid = mp.Value('i', 0)
    generator_threads = mp.Value('i', 0)
    generator_switches_per_thread = mp.Value('i', 0)
    generator_thread_creation_delay_ms = mp.Value('i', 0)
    generator_delay_before_traffic_ms = mp.Value('i', 0)
    generator_simulated_hosts = mp.Value('i', 0)
    generator_switches = mp.Value('i', 0)
    global_sample_id = mp.Value('i', 0)

    logging.info('[active_test] Initializing test parameters')
    cpu_lists = util.cpu.compute_cpu_shares([conf['controller_cpu_shares'],
                                             conf['generator_cpu_shares']])
    controller_cpus_str = ','.join(str(e) for e in cpu_lists[0])
    generator_cpus_str = ','.join(str(e) for e in cpu_lists[1])
    controller_build = ctrl_base_dir + conf['controller_build']
    controller_start = ctrl_base_dir + conf['controller_start']
    controller_status = ctrl_base_dir + conf['controller_status']
    controller_stop = ctrl_base_dir + conf['controller_stop']
    controller_clean = ctrl_base_dir + conf['controller_clean']
    controller_logs_dir = ctrl_base_dir + conf['controller_logs_dir']
    generator_build = gen_base_dir + conf['generator_build']
    generator_run = gen_base_dir + conf['generator_run']
    generator_clean = gen_base_dir + conf['generator_clean']
    controller_port = conf['controller_port']

    file_list = []
    file_list.append(controller_build)
    file_list.append(controller_start)
    file_list.append(controller_status)
    file_list.append(controller_stop)
    file_list.append(controller_clean)
    file_list.append(generator_build)
    file_list.append(generator_run)
    file_list.append(generator_clean)


    # list of samples: each sample is a dictionary that contains all
    # information that describes a single measurement, i.e.:
    #    - the actual performance results
    #    - secondary runtime statistics
    #    - current values of test dimensions (dynamic)
    #    - test configuration options (static)
    total_samples = []

    try:
        # Before procceeding with the experiments check validity of all handlers
        f = util.file.check_files_exist(file_list)
        if f != []:
            raise Exception('Files {0} do not exist.'.format(f))

        f = util.file.check_files_executables(file_list)
        if f != []:
            raise Exception('Files {0} are not executable.'.format(f))

        if conf['generator_rebuild']:
            logging.info('[active_test] Building generator')
            cp.check_output_streaming([generator_build], '[generator_build]')

        if conf['controller_rebuild']:
            logging.info('[active_test] Building controller')
            cp.check_output_streaming([controller_build], '[controller_build]')

        logging.info((
            '[active_test] Checking if another controller is listening on '
            'specified port'))
        cpid.value = util.process.get_pid_listening_on_port(controller_port)
        if cpid.value != -1:
            raise Exception(
                'Another controller is active on port {0}'.format(controller_port))

        os.environ['JAVA_OPTS'] = ' '.join(conf['java_opts'])

        logging.info('[active_test] Starting controller')
        cp.check_output_streaming(
            ['taskset', '-c', controller_cpus_str, controller_start],
            '[controller_start]')

        logging.info('[active_test] Waiting until controller starts listening')
        cpid.value = common.wait_until_controller_listens(7, controller_port)
        logging.info('[active_test] Controller pid: {0}'.format(cpid.value))

        logging.info('[active_test] Checking controller status after starting')
        out = sp.check_output([controller_status]).strip()
        if out == '0':
            raise Exception('Controller failed to start')
        logging.info('[active_test] OK, controller status is 1.')

        # run tests for all possible dimensions
        for (generator_threads.value,
             generator_switches_per_thread.value,
             generator_thread_creation_delay_ms.value,
             generator_delay_before_traffic_ms.value,
             generator_simulated_hosts.value,
             repeat_id.value) in itertools.product(
                                    conf['generator_threads'],
                                    conf['generator_switches_per_thread'],
                                    conf['generator_thread_creation_delay_ms'],
                                    conf['generator_delay_before_traffic_ms'],
                                    conf['generator_simulated_hosts'],
                                    range(0, conf['test_repeats'])):

            generator_switches.value = generator_threads.value * \
                                       generator_switches_per_thread.value

            logging.debug('[active_test] Creating data and control queues')
            dq = mp.Queue()
            rq = mp.Queue()

            logging.debug('[active_test] Creating monitor thread')
            mt = mp.Process(target=monitor,
                            args=(dq,
                                  rq,
                                  conf,
                                  cpid,
                                  global_sample_id,
                                  repeat_id,
                                  generator_switches,
                                  generator_switches_per_thread,
                                  generator_threads,
                                  generator_delay_before_traffic_ms,
                                  generator_thread_creation_delay_ms,
                                  generator_simulated_hosts))

            logging.debug('[active_test] Creating generator thread')
            gt = mp.Process(
                target=common.generator,
                args=(generator_run,
                      generator_cpus_str,
                      conf['controller_ip'],
                      controller_port,
                      generator_threads.value,
                      generator_switches_per_thread.value,
                      generator_switches.value,
                      generator_thread_creation_delay_ms.value,
                      generator_delay_before_traffic_ms.value,
                      conf['generator_ms_per_test'],
                      conf['generator_internal_repeats'],
                      generator_simulated_hosts.value,
                      conf['generator_warmup'],
                      conf['generator_mode'],
                      dq,
                      _term_success,
                      _term_fail))

            mt.start()
            gt.start()

            samples = rq.get(block=True)
            total_samples = total_samples + samples

            logging.debug('[active_test] Joining monitor thread')
            mt.join()
            logging.debug('[active_test] Joining generator thread')
            gt.join()

            if conf['controller_restart']:
                if sp.check_output([controller_status]).strip() == '1':
                    cp.check_output_streaming([controller_stop],
                                              '[controller_stop]')
                    common.wait_until_process_finishes(cpid.value)

                cp.check_output_streaming(
                    ['taskset', '-c', controller_cpus_str, controller_start],
                    '[controller_start]')
                cpid.value = common.wait_until_controller_listens(
                    7,
                    controller_port)

    except:
        logging.error('[active_test] :::::::::: Exception caught :::::::::::')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error('[active_test] Exception: {0}, {1}'.format(
            exc_type, exc_tb.tb_lineno))

        errors = str(exc_obj).rstrip().split('\n')
        for error in errors:
            logging.error('[active_test] ' + error)

    finally:
        logging.info('[active_test] Finalizing test')

        if len(total_samples) > 0:
            with open(out_json, 'w') as ojf:
                json.dump(total_samples, ojf)
            ojf.close()

        if sp.check_output([controller_status]).strip() == '1':
            logging.info('[active_test] Stopping controller')
            cp.check_output_streaming([controller_stop], '[controller_stop]')

        if os.path.isdir(controller_logs_dir):
            logging.info('[active_test] Collecting logs')
            shutil.move(controller_logs_dir, output_dir)

        if conf['controller_cleanup']:
            logging.info('[active_test] Cleaning controller')
            cp.check_output_streaming([controller_clean], '[controller_clean]')

        if conf['generator_cleanup']:
            logging.info('[active_test] Cleaning generator')
            cp.check_output_streaming([generator_clean], '[generator_clean]')
