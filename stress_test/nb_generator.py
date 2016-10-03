# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NB-Generator Class- All NB-Generator-related functionality is here"""

import logging
import time
# import stress_test.controller
# import stress_test.emulator
import multiprocessing
import util.netutil


class NBgen:

    def __init__(self, nb_gen_base_dir, test_config, controller, multinet):
        """Create an NB-generator object. Options from JSON input file
        :param test_config: JSON input configuration
        :param nb_gen_base_dir: emulator base directory
        :type test_config: JSON configuration dictionary
        :type nb_gen_base_dir: str
        """
        self.controller = controller
        self.multinet = multinet
        self.name = test_config['nb_generator_name']
        self.base_dir = nb_gen_base_dir

        self.cpus = test_config['nb_generator_cpu_shares']
        # self.host_spec = test_config['nb_generator_node_spec']
        # self.host_ip = test_config['nb_generator_host_ip']

        self.ip = test_config['nb_generator_ode_ip']
        self.ssh_port = test_config['nb_generator_node_ssh_port']
        self.ssh_user = test_config['nb_generator_node_username']
        self.ssh_pass = test_config['nb_generator_node_password']

        self.run_hnd = (self.base_dir +
                        test_config['nb_generator_run_handler'])
        self.status = 'UNKNOWN'
        self._ssh_conn = None

        self.flow_delete_flag = test_config['flow_delete_flag']
        self.flows_per_request = test_config['flows_per_request']
        self.log_level

        # The parameters initialized as None are dimensions of the test.
        # These values are passed outside, from the test in the main for loop.
        # ---------------------------------------------------------------------
        self.flow_workers = None
        self.total_flows = None
        self.flow_operations_delay_ms = None
        # ---------------------------------------------------------------------

    def init_ssh(self):
        logging.info(
            '[open_ssh_connection] Initiating SSH session with {0} node.'.
            format(self.name, self.ip))

        self._ssh_conn = \
            util.netutil.ssh_connect_or_return2(self.ip,
                                                int(self.ssh_port),
                                                self.ssh_user,
                                                self.ssh_pass,
                                                10)

    def run(self):
        """ Wrapper to the NB-Generator run handler
        :returns: Returns the combined stdout - stderr of the executed command
        :rtype: str
        """
        logging.info("[NB_generator] Run handler")
        cmd = ('cd {0}; taskset -c {1} python3.4 {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12}'.
               format(self.base_dir,
                      self.cpus,
                      self.run_hnd,
                      self.controller.ip,
                      self.controller.restconf_port,
                      self.total_flows,
                      self.flow_workers,
                      self.flow_operations_delay_ms,
                      self.flow_delete_flag,
                      self.controller.restconf_user,
                      self.controller.restconf_pass,
                      self.flows_per_request,
                      self.log_level))
        logging.debug('Generator handler command:{0}.'.format(cmd))

        exit_status, output = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         cmd,
                                         '[NB_generator_run_handler]')
        if exit_status == 0:
            self.status = 'RUNNING'
            logging.info("[NB_generator] Successful started")
        else:
            self.status = 'NOT_RUNNING'
            raise Exception('[NB_generator] Failure during starting')

        return output

    def poll_flows_ds(self, result_queue, t_start):
        """
        Monitors operational DS until the expected number of flows are
        found or the deadline is reached.
        :param t_start: timestamp for begin of discovery
        :returns: Returns a float number containing the time in which
        total flows were discovered otherwise containing -1.0 on failure.
        :rtype: float
        :type t_start: float
        """
        deadline = 240
        t_discovery_start = time.time()
        previous_discovered_flows = 0
        while True:
            if (time.time() - t_discovery_start) > deadline:
                logging.info('[NB_generator] Deadline of {0} seconds '
                             'passed'.format(deadline))
                result_queue.put({'end_to_end_flows_operation_time': -1.0},
                                 block=True)
                return
            else:
                oper_ds_found_flows = self.controller.get_oper_hosts()
                if (oper_ds_found_flows - previous_discovered_flows) != 0:
                    t_discovery_start = time.time()
                    previous_discovered_flows = oper_ds_found_flows
                if oper_ds_found_flows == self.total_flows:
                    time_interval = time.time() - t_start
                    logging.debug('[NB_generator] Flow-Master '
                                  '{0} flows found in {1} seconds'.
                                  format(self.total_flows, time_interval))
                    result_queue.put({'end_to_end_flows_operation_time':
                                      time_interval}, block=True)
                    return
            time.sleep(1)


def poll_flows_ds_confirm(self, result_queue):
    """
    Monitors operational DS until the expected number of flows are found
    or the deadline is reached.
    :returns: Returns a float number containing the time in which
    total flows were discovered otherwise containing -1.0 on failure.
    :rtype: float
    """
    deadline = 240
    t_discovery_start = time.time()
    t_start = time.time()
    previous_discovered_flows = 0
    while True:
        if (time.time() - t_discovery_start) > deadline:
            logging.info('[NB_generator] Deadline of {0} seconds '
                         'passed'.format(deadline))
            result_queue.put({'confirm_time': -1.0}, block=True)
            return
        else:
            oper_ds_found_flows = self.controller.get_oper_hosts()
            logging.debug('[NB_generator] Found {0} flows at inventory'.
                          format(oper_ds_found_flows))
            if (oper_ds_found_flows - previous_discovered_flows) != 0:
                t_discovery_start = time.time()
                previous_discovered_flows = oper_ds_found_flows
            if oper_ds_found_flows == self.total_flows:
                time_interval = time.time() - t_start
                logging.debug('[NB_generator] Flow-Master '
                              '{0} flows found in {1} seconds'.
                              format(self.total_flows, time_interval))
                result_queue.put({'confirm_time': time_interval}, block=True)
                return
        time.sleep(1)


def poll_flows_switches(self, result_queue, t_start):
    """
    Monitors operational flows in switches of Multinet until the expected
    number of flows are found or the deadline is reached.
    :param t_start: timestamp for begin of discovery
    :returns: Returns a float number containing the time in which
    total flows were discovered otherwise containing -1.0 on failure.
    :rtype: float
    :type t_start: float
    """
    deadline = 240
    t_discovery_start = time.time()
    previous_discovered_flows = 0
    while True:
        if (time.time() - t_discovery_start) > deadline:
            logging.info('[NB_generator] Deadline of {0} seconds '
                         'passed'.format(deadline))
            result_queue.put({'switch_operation_time': -1.0}, block=True)
            return
        else:
            discovered_flows = self.multinet.get_flows()
            logging.debug('[NB_generator] Found {0} flows at topology switches'
                          .format(discovered_flows))
            if (discovered_flows - previous_discovered_flows) != 0:
                t_discovery_start = time.time()
                previous_discovered_flows = discovered_flows
            if discovered_flows == self.total_flows:
                time_interval = time.time() - t_start
                logging.debug('[NB_generator] expected flows = {0} \n '
                              'discovered flows = {1}'.
                              format(self.total_flows, discovered_flows))
                result_queue.put({'switch_operation_time': time_interval},
                                 block=True)
                return
        time.sleep(1)
    return


def monitor_threads_run(self, t_start):
    """
    Monitors operational flows in switches of Multinet until the expected
    number of flows are found or the deadline is reached.
    :param t_start: timestamp for begin of discovery
    :returns: Returns a float number containing the time in which
    total flows were discovered otherwise containing -1.0 on failure.
    :rtype: float
    :type t_start:
    """

    logging.info('[NB_generator] creating result queues for ...')
    result_queue = multiprocessing.Queue()
    logging.info('[NB_generator]creating thread for '
                 'end_to_end_installation_time measurement')
    monitor_thread_ds = multiprocessing.Process(target=self.poll_flows_ds,
                                                args=(result_queue, t_start))

    monitor_thread_sw = \
        multiprocessing.Process(target = self.poll_flows_switches,
                                args=(result_queue, t_start))
    monitor_thread_ds_confirm = \
        multiprocessing.Process(target= self.poll_flows_ds_confirm,
                                args=result_queue)
    monitor_thread_ds.start()
    monitor_thread_sw.start()
    monitor_thread_ds_confirm.start()

    monitor_thread_ds.join()
    monitor_thread_sw.join()
    monitor_thread_ds_confirm.join()

    t_start = time.time()
    discovered_flows = self.multinet.get_flows()
    flows_measurement_latency_interval = time.time() - t_start
    logging.info('[NB_generator] Flows measurement latency'
                 'interval:{0} [sec] | Discovered flows:{1}'.
                 format(flows_measurement_latency_interval, discovered_flows))
    results = {}
    while not result_queue.empty():
        results.update(result_queue.get())
    return results