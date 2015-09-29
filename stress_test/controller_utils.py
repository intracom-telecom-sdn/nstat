# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Reusable functions for processes that are controller related """

import common
import logging
import subprocess
import time
import util.customsubprocess
import util.process

def rebuild_controller(controller_build_handler):
    """ Wrapper to the controller build handler

    :param controller_build_handler: filepath to the controller build handler
    :type controller_build_handler: str
    """

    util.customsubprocess.check_output_streaming([controller_build_handler],
                                                 '[controller_build_handler]')


def start_controller(controller_start_handler, controller_status_handler,
                     controller_port, controller_cpus_str):
    """Wrapper to the controller start handler

    :param controller_start_handler: filepath to the controller start handler
    :param controller_status_handler: filepath to the controller status handler
    :param controller_port: controller port number to listen for SB connections
    :param controller_cpus_str: controller CPU share as a strin containing
                                the values of shares, separated with coma
    :returns: controller's process ID
    :raises Exception: When controller fails to start.
    :rtype: int
    :type controller_start_handler: str
    :type controller_status_handler: str
    :type controller_port: int
    :type controller_cpus_str: str
    """

    if check_controller_status(controller_status_handler) == '0':
        util.customsubprocess.check_output_streaming(
            ['taskset', '-c', controller_cpus_str, controller_start_handler],
            '[controller_start_handler]')
        logging.info(
            '[start_controller] Waiting until controller starts listening')
        cpid = wait_until_controller_listens(420000, controller_port)
        logging.info('[start_controller] Controller pid: {0}'.format(cpid))
        logging.info(
            '[start_controller] Checking controller status after it starts '
            'listening on port {0}.'.format(controller_port))
        wait_until_controller_up_and_running(420000, controller_status_handler)
        return cpid
    else:
        logging.info('[start_controller] Controller already started.')


def cleanup_controller(controller_clean_handler):
    """Wrapper to the controller cleanup handler

    :param controller_clean_handler: filepath to the controller cleanup handler
    :type controller_clean_handler: str
    """

    util.customsubprocess.check_output_streaming([controller_clean_handler],
                                                 '[controller_clean_handler]')


def stop_controller(controller_stop_handler, controller_status_handler, cpid):
    """Wrapper to the controller stop handler


    :param controller_stop_handler: filepath to the controller stop handler
    :param controller_status_handler: filepath to the controller status handler
    :param cpid: controller process ID
    :type controller_stop_handler: str
    :type controller_status_handler: str
    :type cpid: int
    """

    if check_controller_status(controller_status_handler) == '1':
        logging.debug('[stop_controller] Stopping controller.')
        util.customsubprocess.check_output_streaming(
            [controller_stop_handler], '[controller_stop_handler]')
        util.process.wait_until_process_finishes(cpid)
    else:
        logging.debug('[stop_controller] Controller already stopped.')


def check_controller_status(controller_status_handler):
    """Wrapper to the controller status handler

    :param controller_status_handler: filepath to the controller status handler
    :returns: '1' if controller is active, '0' otherwise
    :rtype: str
    :type controller_status_handler: str
    """

    return subprocess.check_output([controller_status_handler],
                                   universal_newlines=True).strip()


def controller_changestatsperiod(controller_statistics_handler,
                                 stat_period_ms):
    """Wrapper to the controller statistics handler

    :param controller_statistics_handler: filepath to the controller statistics
                                          handler
    :param stat_period_ms: statistics period value to set (in milliseconds)
    :type controller_statistics_handler: str
    :type curr_stat_period: int
    """

    util.customsubprocess.check_output_streaming(
        [controller_statistics_handler, str(stat_period_ms)],
        '[controller_statistics_handler] Changing statistics interval')
    logging.info(
        '[controller_changestatsperiod] Changed statistics period to {0} ms'.
        format(stat_period_ms))


def restart_controller(controller_stop_handler, controller_start_handler,
                       controller_status_handler, controller_port, old_cpid,
                       controller_cpus_str):
    """Restarts the controller

    :param controller_start: filepath to the controller start handler
    :param controller_status: filepath to the controller status handler
    :param controller_stop: filepath to the controller stop handler
    :param controller_port: controller port number to listen for SB connections
    :param old_cpid: PID of already running controller process
    :param controller_cpus_str: controller CPU share as a strin containing
                                the values of shares, separated with comma
    :returns: controller process ID
    :rtype: int
    :type controller_start: str
    :type controller_status: str
    :type controller_stop: str
    :type controller_port: int
    :type old_cpid: int
    :type controller_cpus_str: str
    """

    stop_controller(controller_stop_handler, controller_status_handler,
                    old_cpid)
    new_cpid = start_controller(controller_start_handler,
        controller_status_handler, controller_port, controller_cpus_str)
    return new_cpid


def check_for_active_controller(controller_port):
    """Checks for processes listening on the specified port

    :param controller_port: controller port to check
    :raises Exception: When another process Listens on controller's port.
    :type controller_port: int
    """

    logging.info(
        '[check_for_active_controller] Checking if another process is '
        'listening on specified port. Port number: {0}.'.
        format(controller_port))

    cpid = util.process.getpid_listeningonport(controller_port)

    if cpid != -1:
        raise Exception('[check_for_active_controller] Another process is '
                        'active on port {0}'.
                        format(controller_port))
    return cpid


def wait_until_controller_listens(interval_ms, port):
    """ Waits for the controller to start listening on specified port.

    :param interval_ms: milliseconds to wait (in milliseconds).
    :param port: controller port.
    :raises Exception: If controller fails to start or if another process
    listens on controllers port.
    :returns: on success, returns the controller pid.
    :rtype int
    :type interval_ms: int
    :type port: int
    """

    timeout = time.time() + (float(interval_ms) / 1000)
    while time.time() < timeout:
        time.sleep(1)
        pid = util.process.getpid_listeningonport(port)
        logging.debug('Returned pid listening on port {0}: {1}'.
                      format(port, pid))

        if pid > 0:
            return pid
        elif pid == 0:
            raise Exception('Another controller seems to have started in the '
                            'meantime. Exiting...')

    raise Exception('Controller failed to start within a period of {0} '
                    'minutes'.format(timeout))


def wait_until_controller_up_and_running(interval_ms, controller_status_handler):
    """ Waits for the controller status to become 1 (Started).

    :param interval_ms: milliseconds to wait (in milliseconds).
    :param controller_status_handler: filepath to the controller status handler
    :raises Exception: If controller fails to start or if another process
    listens on controllers port.
    :type interval_ms: int
    :type controller_status_handler: str
    """

    timeout = time.time() + (float(interval_ms) / 1000)
    while time.time() < timeout:
        time.sleep(1)
        if check_controller_status(controller_status_handler) == '1':
            return

    raise Exception('Controller failed to start. '
                    'Status check returned 0 after trying for {0} seconds.'.
                    format(float(interval_ms) / 1000))

