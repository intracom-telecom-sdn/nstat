# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Reusable functions for southbound tests """

import logging
import subprocess as sp
import time
import util.customsubprocess as cp
import util.process
import util.sysstats as sysstat

def wait_until_controller_listens(minutes, port):
    """ Waits for the controller to start listening on specified port.
        :param minutes: minutes to wait
        :param port: controller port
        :returns: on success, returns the controller pid. On failure,
                  it raises an exception
    """
    timeout = time.time() + 60*minutes
    while time.time() < timeout:
        time.sleep(1)
        pid = util.process.get_pid_listening_on_port(port)
        logging.debug('Returned pid listening on port {0}: {1}'.\
            format(port, pid))
        if pid > 0:
            return pid
        elif pid == 0:
            raise Exception((
                'Another controller seems to have started in the meantime.'
                ' Exiting...'))

    raise Exception((
        'Controller failed to start within a period of {0} '
        'minutes').format(minutes))


def wait_until_process_finishes(pid):
    """ Waits until the process with the specified ID finishes
    :param pid: process id
    """

    while util.process.is_process_running(pid):
        time.sleep(1)


def sample_stats(cpid):
    """ Take runtime statistics
    :param cpid: controller PID
    :returns: the statistics in a dictionary
    """

    s = {}
    s['total_memory_bytes'] = sysstat.sys_total_memory_bytes()
    s['controller_cwd'] = sysstat.proc_cwd(cpid)
    s['controller_java_xopts'] = [o for o in \
                                  sysstat.proc_cmdline(cpid) if \
                                  o.startswith('-X')]
    s['timestamp'] = int(sp.check_output('date +%s', shell=True).strip())
    s['date'] = sp.check_output('date', shell=True).strip()
    s['used_memory_bytes'] = sysstat.sys_used_memory_bytes()
    s['free_memory_bytes'] = sysstat.sys_free_memory_bytes()
    s['controller_cpu_system_time'] = sysstat.proc_cpu_system_time(cpid)
    s['controller_cpu_user_time'] = sysstat.proc_cpu_user_time(cpid)
    s['controller_vm_size'] = sysstat.proc_vm_size(cpid)
    s['controller_num_fds'] = sysstat.proc_num_fds(cpid)
    s['controller_num_threads'] = sysstat.proc_num_threads(cpid)
    s['one_minute_load'] = sysstat.sys_load_average()[0]
    s['five_minute_load'] = sysstat.sys_load_average()[1]
    s['fifteen_minute_load'] = sysstat.sys_load_average()[2]
    return s


def generator(
        run_handler, generator_cpus, controller_ip, controller_port, threads,
        sw_per_thread, switches, thr_delay, traf_delay, ms_per_test,
        internal_repeats, hosts, warmup, mode, dq=None, succ_msg='',
        fail_msg=''):
    """ Function executed by generator thread.

    :param run_handler: generator run handler
    :param generator_cpus: A comma separated string with the cpu ids we assign
           on generator.
    :param controller_ip: controller IP for OpenFlow connection
    :param controller_port: controller port for OpenFlow connection
    :param threads: number of generator threads
    :param sw_per_thread: number of switches per thread
    :param switches: number of total switches
    :param thr_delay: delay between thread creation
    :param traf_delay: delay between last thread creation and traffic transmission
    :param ms_per_test: test duration of a single generator loop
    :param internal_repeats: number of generator loops
    :param hosts: number of simulated hoss
    :param warmup: initial loops to be considered as 'warmup'
    :param mode: generator mode
    :param dq: data queue where generator output is posted line by line
    """

    logging.debug('[generator_thread] Generator thread started')

    try:
        cp.check_output_streaming(
            ['taskset', '-c', generator_cpus, run_handler,
            controller_ip, str(controller_port), str(threads),
            str(sw_per_thread), str(switches), str(thr_delay),
            str(traf_delay), str(ms_per_test), str(internal_repeats),
            str(hosts), str(warmup), mode],
            '[generator_thread]', dq)

        # generator ended, enqueue termination message
        if dq is not None:
            dq.put(succ_msg, block=True)
        logging.debug('[generator_thread] Generator thread ended successfully')
    except sp.CalledProcessError as e:
        if dq is not None:
            dq.put(fail_msg, block=True)
        logging.error('[generator_thread] Exception:' + str(e))

    return
