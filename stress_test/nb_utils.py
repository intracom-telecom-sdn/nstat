# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NSTAT NorthBound  """

import emulators.nb_generator.flow_utils
import logging
import multinet_utils
import multiprocessing
import time
import util.netutil

def get_operational_ds_flows(controller_nb_interface):
    """description """
    odl_inventory = emulators.nb_generator.flow_utils.FlowExplorer(controller_nb_interface.ip,
                                                         controller_nb_interface.port,
                                                         'operational',
                                                         (controller_nb_interface.username, controller_nb_interface.password))
    odl_inventory.get_inventory_flows_stats()
    logging.debug('Found {0} flows at inventory'.
                  format(odl_inventory.found_flows))
    return odl_inventory.found_flows




def nb_generator_start(nb_generator_ssh_client,nb_generator_base_dir,nb_generator_cpus,
                       nb_generator_handlers_set,controller_node,
                       controller_nb_interface,total_flows,flow_workers,
                       flow_operations_delay_ms,flow_delete_flag,log_level):
    cmd = ('cd {0}; taskset -c {1} python3.4 {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}'.
           format(nb_generator_base_dir, nb_generator_cpus,
                  nb_generator_handlers_set.run_handler,
                  controller_node.ip, controller_nb_interface.port,
                  total_flows, flow_workers, flow_operations_delay_ms,
                  flow_delete_flag, controller_nb_interface.username,
                  controller_nb_interface.password, log_level))
    logging.debug('Generator handler command:{0}.'.format(cmd))

    exit_status , output = util.netutil.ssh_run_command(nb_generator_ssh_client,
                                                        cmd,
                                                        '[generator_run_handler]')

    if exit_status!=0:
        raise Exception('northbound generator failed')

    return output


def poll_flows_dastastore(result_queue, expected_flows, t_start, controller_nb_interface):
    """
    Monitors operational DS until the expected number of flows are found or the
    deadline is reached.

    :param expected_flows: expected number of flows
    :param ctrl_ip: controller IP
    :param ctrl_port: controller RESTconf port
    :param t_start: timestamp for begin of discovery
    :param auth_token: RESTconf authorization token (username/password tuple)

    :returns: Returns a float number containing the time in which
    expected_flows were discovered otherwise containing -1.0 on failure.
    flow_transmission_start
    :rtype: float
    :type expected_flows: int
    :type ctrl_ip: str
    :type ctrl_port: int
    :type t_start: float
    :type auth_token: tuple<str>
    """

    deadline = 240

    t_discovery_start = time.time()
    previous_discovered_flows = 0

    while True:
        if (time.time() - t_discovery_start) > deadline:
            logging.info('[flow_master_thread] Deadline of {0} seconds '
                         'passed'.format(deadline))
            result_queue.put({'end_to_end_flows_operation_time': -1.0}, block=True)
            return
        else:
            operational_ds_found_flows = get_operational_ds_flows(controller_nb_interface)
            if (operational_ds_found_flows - previous_discovered_flows) != 0:
                t_discovery_start = time.time()
                previous_discovered_flows = operational_ds_found_flows
            if operational_ds_found_flows == expected_flows:
                time_interval = time.time() - t_start
                logging.debug('[flow_master_thread] Flow-Master '
                             '{0} flows found in {1} seconds'.
                             format(expected_flows, time_interval))

                result_queue.put({'end_to_end_flows_operation_time': time_interval}, block=True)

                return

        time.sleep(1)


def poll_flows_dastastore_confirm(result_queue, expected_flows, controller_nb_interface):
    """
    Monitors operational DS until the expected number of flows are found or the
    deadline is reached.

    :param expected_flows: expected number of flows
    :param ctrl_ip: controller IP
    :param ctrl_port: controller RESTconf port
    :param t_start: timestamp for begin of discovery
    :param auth_token: RESTconf authorization token (username/password tuple)

    :returns: Returns a float number containing the time in which
    expected_flows were discovered otherwise containing -1.0 on failure.
    flow_transmission_start
    :rtype: float
    :type expected_flows: int
    :type ctrl_ip: str
    :type ctrl_port: int
    :type t_start: float
    :type auth_token: tuple<str>
    """

    deadline = 240

    t_discovery_start = time.time()
    t_start = time.time()
    previous_discovered_flows = 0

    while True:
        if (time.time() - t_discovery_start) > deadline:
            logging.info('[flow_master_thread] Deadline of {0} seconds '
                         'passed'.format(deadline))
            result_queue.put({'confirm_time': -1.0}, block=True)
            return
        else:
            operational_ds_found_flows = get_operational_ds_flows(controller_nb_interface)
            logging.debug('Found {0} flows at inventory'.
                          format(operational_ds_found_flows))
            if (operational_ds_found_flows - previous_discovered_flows) != 0:
                t_discovery_start = time.time()
                previous_discovered_flows = operational_ds_found_flows
            if operational_ds_found_flows == expected_flows:
                time_interval = time.time() - t_start
                logging.debug('[flow_master_thread] Flow-Master '
                             '{0} flows found in {1} seconds'.
                             format(expected_flows, time_interval))

                result_queue.put({'confirm_time': time_interval}, block=True)

                return

        time.sleep(1)


def poll_flows_switches(result_queue, expected_flows, t_start,get_flows_handler,
                        multinet_base_dir):
    deadline = 240
    t_discovery_start = time.time()
    previous_discovered_flows = 0

    while True:
        if (time.time() - t_discovery_start) > deadline:
            logging.info('[flow_master_thread] Deadline of {0} seconds '
                         'passed'.format(deadline))
            result_queue.put({'switch_operation_time': -1.0}, block=True)
            return
        else:
            discovered_flows = multinet_utils.get_topology_flows(multinet_base_dir,
                                                  get_flows_handler)
            logging.debug('Found {0} flows at topology switches'.
                          format(discovered_flows))
            if (discovered_flows - previous_discovered_flows) != 0:
                t_discovery_start = time.time()
                previous_discovered_flows = discovered_flows
            if discovered_flows == expected_flows:
                time_interval = time.time() - t_start
                logging.debug('expected flows = {0} \n '
                             'discovered flows = {1}'.
                             format(expected_flows, discovered_flows))

                result_queue.put({'switch_operation_time': time_interval}, block=True)

                return

        time.sleep(1)
    return


def monitor_threads_run(expected_flows, t_start, controller_nb_interface,
                        get_flows_handler,multinet_base_dir):

    logging.info('creating result queues for ...')
    result_queue = multiprocessing.Queue()
    logging.info('creating thread for end_to_end_installation_time measurement')
    monitor_thread_ds = multiprocessing.Process(target=poll_flows_dastastore,
                                             args=(result_queue,expected_flows,
                                                  t_start,
                                                  controller_nb_interface))
    monitor_thread_sw = multiprocessing.Process(target=poll_flows_switches,
                                             args=(result_queue,expected_flows,
                                                  t_start,get_flows_handler,
                                                  multinet_base_dir))
    monitor_thread_ds_confirm = multiprocessing.Process(target=poll_flows_dastastore_confirm,
                                             args=(result_queue,expected_flows,
                                                   controller_nb_interface))
    monitor_thread_ds.start()
    monitor_thread_sw.start()
    monitor_thread_ds_confirm.start()

    monitor_thread_ds.join()
    monitor_thread_sw.join()
    monitor_thread_ds_confirm.join()
    results = {}
    while not result_queue.empty():
        results.update(result_queue.get())

    return results

