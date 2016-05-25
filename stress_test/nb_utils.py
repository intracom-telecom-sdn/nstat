# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NSTAT NorthBound  """

import emulators.nb_generator.flow_utils
import logging
import time

def nb_generator_start(nb_generator_base_dir,nb_generator_cpus,
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


def poll_flows(expected_flows, t_start, controller_nb_interface):
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
    odl_inventory = emulators.nb_generator.flow_utils.FlowExplorer(controller_nb_interface.ip,
                                                         controller_nb_interface.port,
                                                         'operational',
                                                         (controller_nb_interface.username, controller_nb_interface.password))
    t_discovery_start = time.time()
    previous_discovered_flows = 0

    while True:
        if (time.time() - t_discovery_start) > deadline:
            logging.info('[flow_master_thread] Deadline of {0} seconds '
                         'passed'.format(deadline))
            return -1.0

        else:
            odl_inventory.get_inventory_flows_stats()
            logging.debug('Found {0} flows at inventory'.
                          format(odl_inventory.found_flows))
            if (odl_inventory.found_flows - previous_discovered_flows) != 0:
                t_discovery_start = time.time()
                previous_discovered_flows = odl_inventory.found_flows
            if odl_inventory.found_flows == expected_flows:
                time_interval = time.time() - t_start
                logging.debug('[flow_master_thread] Flow-Master '
                             '{0} flows found in {1} seconds'.
                             format(expected_flows, time_interval))

                return time_interval

        time.sleep(1)

