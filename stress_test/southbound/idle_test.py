# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Idle Southbound Performance test """

import common
import itertools
import json
import logging
import multiprocessing as mp
import os
import requests
import shutil
import sys
import subprocess as sp
import time
import util.cpu
import util.customsubprocess as cp
import util.file
import util.process

# termination messages sent from monitor thread to main in order to
# kill generator, either when it fails to make its switches visible
# to the controller, or not
_term_gen_fail_ = '__kill_failed_generator__'
_term_gen_succ_ = '__kill_successful_generator__'

def check_ds_switches(controller_ip, controller_port, auth_user, auth_pass):
    """ Return number of switches found in ODL controller datastore

    :param controller_ip: ODL controller IP
    :param controller_port: controller restconf port
    :param auth_user: restconf user
    :param auth_pass: restconf password
    :returns: number of switches found, 0 if none exists
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/').\
        format(controller_ip, controller_port)

    try:
        d = requests.get(url=url, auth=(auth_user, auth_pass)).json()['topology'][0]
    except:
        return 0

    if d.has_key('node'):
        return len(d['node'])
    else:
        return 0


def monitor(conf, sleep_secs, expected_switches, discovery_deadline, q):
    """ Function executed by the monitor thread

    :param conf: test configuration
    :param sleep_secs: seconds to sleep before starting querying the DS for
                       switches installed
    :param expected_switches: switches expected to find in the DS
    :param discovery_deadline: deadline (in secs) at which the thread should discover
                         switches
    :param q: queue for communicating with the main context
    """
    logging.debug('[monitor_thread] Monitor thread started')
    t_start = time.time()
    logging.debug(
        '[monitor_thread] Sleeping for {0} seconds'.format(sleep_secs))
    time.sleep(sleep_secs)
    logging.debug('[monitor_thread] Starting discovery')
    t_discovery_start = time.time()
    discovered_switches = 0


    while True:

        if (time.time() - t_discovery_start) > discovery_deadline:
            logging.debug((
                '[monitor_thread] Deadline of {0} seconds passed, discovered '
                '{1} switches.').format(discovery_deadline, discovered_switches))
            q.put((_term_gen_fail_, -1.0, discovered_switches))
            return
        else:
            discovered_switches = check_ds_switches(
                conf['controller_ip'], conf['controller_restconf_port'],
                conf['controller_restconf_user'],
                conf['controller_restconf_password'])

            if discovered_switches == expected_switches:
                dt = time.time() - t_start
                logging.info(
                    '[monitor_thread] {0} switches found in {1} seconds'.\
                    format(discovered_switches, dt))
                q.put((_term_gen_succ_, time.time()-t_start, discovered_switches))
                return
        time.sleep(1)


def idle_test_run(out_json, ctrl_base_dir, gen_base_dir, conf, output_dir):
    """
    Run test
    :param out_json: the JSON output file
    :param ctrl_base_dir: Test base directory
    :param gen_base_dir: Test base directory
    :param conf: JSON configuration dictionary
    :param output_dir: directory to store output files
    """

    # Global variables read-write shared between monitor-main thread.
    cpid = 0
    generator_threads = 0
    generator_switches_per_thread = 0
    generator_thread_creation_delay_ms = 0
    generator_switches = 0
    global_sample_id = 0

    logging.info('[idle_test] Initializing test parameters')

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

    # list of samples: each sample is a dictionary that contains all information
    # that describes a single measurement, i.e.:
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
            logging.info('[idle_test] Building generator')
            cp.check_output_streaming([generator_build], '[generator_build]')

        if conf['controller_rebuild']:
            logging.info('[idle_test] Building controller')
            cp.check_output_streaming([controller_build], '[controller_build]')

        logging.info((
            '[idle_test] Checking if another controller is listening '
            'on specified port'))
        cpid = util.process.get_pid_listening_on_port(controller_port)
        if cpid != -1:
            raise Exception(
                'Another controller is active on port {0}'.\
                format(controller_port))

        os.environ['JAVA_OPTS'] = ' '.join(conf['java_opts'])

        logging.info('[idle_test] Starting controller')

        cp.check_output_streaming(
            ['taskset', '-c', controller_cpus_str,  controller_start],
            '[controller_start]')

        logging.info('[idle_test] Waiting until controller starts listening')
        cpid = common.wait_until_controller_listens(7, controller_port)
        logging.info('[idle_test] Controller pid: {0}'.format(cpid))

        logging.info('[idle_test] Checking controller status after starting')
        out = sp.check_output([ controller_status]).strip()
        if out == '0':
            raise Exception('Controller failed to start')
        logging.info('[idle_test] OK, controller status is 1.')

        # run tests for all possible dimensions
        for (generator_threads,
             generator_switches_per_thread,
             generator_thread_creation_delay_ms) in itertools.product(
                conf['generator_threads'],
                conf['generator_switches_per_thread'],
                conf['generator_thread_creation_delay_ms']):

            generator_switches = generator_threads * \
                                 generator_switches_per_thread

            logging.debug('[idle_test] Creating queue')
            q = mp.Queue()

            sleep_secs = generator_threads * \
                         (generator_thread_creation_delay_ms/1000.0)
            discovery_deadline = 20.0
            logging.debug('[idle_test] Creating monitor thread')
            mt = mp.Process(
                target=monitor,
                args=(conf, sleep_secs, generator_switches,
                      discovery_deadline, q))

            logging.debug('[idle_test] Creating generator thread')
            gt = mp.Process(
                target=common.generator,
                args=(generator_run,
                      generator_cpus_str,
                      conf['controller_ip'],
                      controller_port,
                      generator_threads,
                      generator_switches_per_thread,
                      generator_switches,
                      generator_thread_creation_delay_ms,
                      conf['generator_delay_before_traffic_ms'],
                      conf['generator_ms_per_test'],
                      conf['generator_internal_repeats'],
                      conf['generator_simulated_hosts'],
                      conf['generator_warmup'],
                      conf['generator_mode']))

            mt.start()
            gt.start()

            res = q.get(block=True)

            s = common.sample_stats(cpid)
            s['global_sample_id'] = global_sample_id
            global_sample_id += 1
            s['generator_simulated_hosts'] = conf['generator_simulated_hosts']
            s['generator_switches'] = generator_switches
            s['generator_threads'] = generator_threads
            s['generator_switches_per_thread'] = generator_switches_per_thread
            s['generator_thread_creation_delay_ms'] = generator_thread_creation_delay_ms
            s['generator_delay_before_traffic_ms'] = conf['generator_delay_before_traffic_ms']
            s['controller_ip'] = conf['controller_ip']
            s['controller_port'] = str(conf['controller_port'])
            s['generator_mode'] = conf['generator_mode']
            s['generator_ms_per_test'] = conf['generator_ms_per_test']
            s['generator_internal_repeats'] = conf['generator_internal_repeats']
            s['controller_restart'] = conf['controller_restart']
            s['generator_warmup'] = conf['generator_warmup']
            s['bootup_time_secs'] = res[1]
            s['discovered_switches'] = res[2]

            gt.terminate()
            total_samples.append(s)

            logging.debug('[idle_test] Joining monitor thread')
            mt.join()
            logging.debug('[idle_test] Joining generator thread')
            gt.join()

            if conf['controller_restart']:
                if sp.check_output([ controller_status]).strip() == '1':
                    cp.check_output_streaming(
                        [controller_stop], '[controller_stop]')
                    common.wait_until_process_finishes(cpid)

                cp.check_output_streaming(
                    ['taskset', '-c', controller_cpus_str,
                    controller_start], '[controller_start]')
                cpid = common.wait_until_controller_listens(
                    7, controller_port)

    except:
        logging.error('[idle_test] :::::::::: Exception :::::::::::')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error('[idle_test] Exception: {0}, {1}'.\
            format(exc_type, exc_tb.tb_lineno))

        errors = str(exc_obj).rstrip().split('\n')
        for error in errors:
            logging.error('[idle] ' + error)

    finally:
        logging.info('[idle_test] Finalizing test')

        if len(total_samples) > 0:
            with open(out_json, 'w') as ojf:
                json.dump(total_samples, ojf)
            ojf.close()

        if sp.check_output([ controller_status]).strip() == '1':
            logging.info('[idle_test] Stopping controller')
            cp.check_output_streaming([ controller_stop], '[controller_stop]')

        if os.path.isdir(controller_logs_dir):
            logging.info('[idle_test] Collecting logs')
            shutil.move(controller_logs_dir, output_dir)

        if conf['controller_cleanup']:
            logging.info('[idle_test] Cleaning controller')
            cp.check_output_streaming([ controller_clean], '[controller_clean]')

        if conf['generator_cleanup']:
            logging.info('[idle_test] Cleaning generator')
            cp.check_output_streaming([ generator_clean], '[generator_clean]')
