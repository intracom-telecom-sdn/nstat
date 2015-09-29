# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Reusable functions for processes that are generator related """

import logging
import subprocess
import util.customsubprocess


def rebuild_generator(generator_build_handler):
    """Rebuilds the generator.

    :param generator_build_handler: filepath to the handler that builds the
                                    generator
    :type generator_build_handler: str
    """

    util.customsubprocess.check_output_streaming([generator_build_handler],
                                                 '[generator_build_handler]')


def run_generator(generator_run_handler, generator_cpus, controller_ip,
                  controller_port, threads, sw_per_thread, switches,
                  thr_delay_ms, traf_delay_ms, ms_per_test, internal_repeats,
                  hosts, warmup, mode, data_queue=None):
    """Runs a generator instance

    :param generator_run_handler: generator run handler
    :param generator_cpus: cpu ids we assign to generator (comma separated)
    :param controller_ip: controller IP for OpenFlow connection
    :param controller_port: controller port for OpenFlow connection
    :param threads: number of generator threads
    :param sw_per_thread: number of switches per thread
    :param switches: number of total switches
    :param thr_delay_ms: delay between thread creation (in milliseconds)
    :param traf_delay_ms: delay between last thread creation and traffic
                          transmission (in milliseconds)
    :param ms_per_test: test duration of a single generator loop
    :param internal_repeats: number of generator loops
    :param hosts: number of simulated hoss
    :param warmup: initial loops to be considered as 'warmup'
    :param mode: generator mode
    :param data_queue: data queue where generator output is posted line by line
                       the generator process will run.
    :type generator_run_handler: str
    :type generator_cpus: str
    :type controller_ip: str
    :type controller_port: int
    :type threads: int
    :type sw_per_thread: int
    :type switches: int
    :type thr_delay_ms: int
    :type traf_delay_ms: int
    :type ms_per_test: int
    :type internal_repeats: int
    :type hosts: int
    :type warmup: int
    :type mode: int
    :type data_queue: multiprocessing.Queue
    """

    util.customsubprocess.check_output_streaming(
        ['taskset', '-c', generator_cpus, generator_run_handler, controller_ip,
        str(controller_port), str(threads), str(sw_per_thread),
        str(switches), str(thr_delay_ms), str(traf_delay_ms), str(ms_per_test),
        str(internal_repeats), str(hosts), str(warmup), mode],
        '[generator_run_handler]', data_queue)

def cleanup_generator(generator_clean_handler):
    """Shuts down the Generator.

    :param generator_clean_handler: Filepath to the handler that cleanup the
    generator.
    :type generator_clean_handler: str
    """

    util.customsubprocess.check_output_streaming([generator_clean_handler],
                                                 '[generator_clean_handler]')


def generator_thread(generator_run_handler, generator_cpus, controller_ip,
                     controller_port, threads, sw_per_thread, switches,
                     thr_delay_ms, traf_delay_ms, ms_per_test, internal_repeats,
                     hosts, warmup, mode, data_queue=None, succ_msg='',
                     fail_msg=''):
    """ Function executed by generator thread.

    :param generator_run_handler: generator run handler
    :param generator_cpus: Cpu ids we assign to generator thread
    :param controller_ip: controller IP 
    :param controller_port: controller port 
    :param threads: number of generator threads
    :param sw_per_thread: number of switches per thread
    :param switches: number of total switches
    :param thr_delay: delay between thread creation
    :param traf_delay: delay between last thread creation and traffic
                       transmission
    :param ms_per_test: test duration of a single generator loop
    :param internal_repeats: number of generator loops
    :param hosts: number of simulated hoss
    :param warmup: initial loops to be considered as 'warmup'
    :param mode: generator mode
    :param data_queue: data queue where generator output is posted line by line
    :type generator_run_handler: str
    :type generator_cpus: str
    :type controller_ip: str
    :type controller_port: int
    :type threads: int
    :type sw_per_thread: int
    :type switches: int
    :type thr_delay_ms: int
    :type traf_delay_ms: int
    :type ms_per_test: int
    :type internal_repeats: int
    :type hosts: int
    :type warmup: int
    :type mode: int
    :type data_queue: multiprocessing.Queue
    """

    logging.debug('[generator_thread] Generator thread started')

    try:
        run_generator(generator_run_handler, generator_cpus, controller_ip,
            controller_port, threads, sw_per_thread, switches, thr_delay_ms,
            traf_delay_ms, ms_per_test, internal_repeats, hosts, warmup, mode,
            data_queue)

        # generator ended, enqueue termination message
        if data_queue is not None:
            data_queue.put(succ_msg, block=True)
        logging.debug('[generator_thread] Generator thread ended successfully')
    except subprocess.CalledProcessError as err:
        if data_queue is not None:
            data_queue.put(fail_msg, block=True)
        logging.error('[generator_thread] Exception:{0}'.format(str(err)))

    return
