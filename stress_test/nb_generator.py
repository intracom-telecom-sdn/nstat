# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NB-Generator Class- All NB-Generator-related functionality is here"""

import gevent
from gevent import monkey
import logging
import time
import util.netutil


class NBgen:

    def __init__(self, nb_gen_base_dir, test_config, controller, sbemu,
                 log_level="DEBUG"):
        """Create an NB-generator object. Options from JSON input file
        :param test_config: JSON input configuration
        :param nb_gen_base_dir: emulator base directory
        :param controller: object of the Controller class
        :param sbemu: object of the SBEmu subclass
        :type test_config: JSON configuration dictionary
        :type nb_gen_base_dir: str
        :type controller: object
        :type sbemu: object
        """
        self.controller = controller
        self.sbemu = sbemu
        self.name = test_config['nb_generator_name']
        self.base_dir = nb_gen_base_dir

        self.ip = test_config['nb_generator_node_ip']
        self.ssh_port = test_config['nb_generator_node_ssh_port']
        self.ssh_user = test_config['nb_generator_node_username']
        self.ssh_pass = test_config['nb_generator_node_password']

        self.run_hnd = (self.base_dir +
                        test_config['nb_generator_run_handler'])
        self.status = 'UNKNOWN'
        self._ssh_conn = None

        self.flow_delete_flag = test_config['flow_delete_flag']
        self.flows_per_request = test_config['flows_per_request']
        self.log_level = log_level

        # The parameters initialized as None are dimensions of the test.
        # These values are passed outside, from the test in the main for loop.
        # ---------------------------------------------------------------------
        self.flow_workers = None
        self.total_flows = None
        self.flow_operations_delay_ms = None
        # ---------------------------------------------------------------------
        self.flows_ds_discovery_deadline = 240

        self.confirm_time = 0.0
        self.e2e_installation_time = 0.0
        self.discover_flows_on_switches_time = 0.0

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
        self.status = 'STARTED'
        cmd = ('cd {0}; python3.4 {1} {2} {3} {4} {5} {6} {7} {8} '
               '{9} {10} {11}'.
               format(self.base_dir,
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
            self.status = 'FINISHED'
            logging.info("[NB_generator] Successful ran")
        else:
            self.status = 'FAILED'
            raise Exception('[NB_generator] Failure during running')

        return output

    def __poll_flows_ds(self, t_start):
        """
        Monitors operational DS from the time the transmission starts from NB
        towards the controller until the expected number of flows are
        found or the deadline is reached.
        :param t_start: timestamp for begin of discovery
        :returns: Returns a float number containing the time in which
        total flows were discovered otherwise containing -1.0 on failure.
        :rtype: float
        :type t_start: float
        """
        t_discovery_start = time.time()
        previous_discovered_flows = 0
        while True:
            if (time.time() - t_discovery_start) > \
                    self.flows_ds_discovery_deadline:
                logging.info('[NB_generator] [Poll_flows thread] Deadline of '
                             '{0} seconds passed'
                             .format(self.flows_ds_discovery_deadline))
                self.e2e_installation_time = -1.0
                logging.info('[NB_generator] [Poll_flows thread] End to End '
                             'installation time monitor FAILED')
                return
            else:
                oper_ds_found_flows = self.controller.get_oper_hosts()
                if (oper_ds_found_flows - previous_discovered_flows) != 0:
                    t_discovery_start = time.time()
                    previous_discovered_flows = oper_ds_found_flows
                if oper_ds_found_flows == self.total_flows:
                    time_interval = time.time() - t_start
                    logging.debug('[NB_generator] [Poll_flows thread] Flow-Master '
                                  '{0} flows found in {1} seconds'.
                                  format(self.total_flows, time_interval))
                    self.e2e_installation_time = time_interval
                    logging.info('[NB_generator] [Poll_flows thread] End to End installation time '
                                 'is: {0}'
                                 .format(self.e2e_installation_time))
                    return
            gevent.sleep(1)
#            time.sleep(1)

    def __poll_flows_ds_confirm(self):
        """
        Monitors operational DS until the expected number of flows are found
        or the deadline is reached.
        :returns: Returns a float number containing the time in which
        total flows were discovered otherwise containing -1.0 on failure.
        :rtype: float
        """
        t_start = time.time()
        t_discovery_start = time.time()
        previous_discovered_flows = 0
        while True:
            if (time.time() - t_discovery_start) > \
                    self.flows_ds_discovery_deadline:
                logging.info('[NB_generator] [Poll_flows_confirm thread] Deadline of {0} seconds passed'
                             .format(self.flows_ds_discovery_deadline))
                self.confirm_time = -1.0
                logging.info('[NB_generator] [Poll_flows_confirm thread] Confirmation '
                             'time monitoring FAILED')
                return
            else:
                oper_ds_found_flows = self.controller.get_oper_hosts()
                logging.debug('[NB_generator] [Poll_flows_confirm thread] Found {0} flows at inventory'.
                              format(oper_ds_found_flows))
                if (oper_ds_found_flows - previous_discovered_flows) != 0:
                    t_discovery_start = time.time()
                    previous_discovered_flows = oper_ds_found_flows
                if oper_ds_found_flows == self.total_flows:
                    time_interval = time.time() - t_start
                    logging.debug('[NB_generator] [Poll_flows_confirm thread] Flow-Master '
                                  '{0} flows found in {1} seconds'.
                                  format(self.total_flows, time_interval))
                    self.confirm_time = time_interval
                    logging.info('[NB_generator] [Poll_flows_confirm thread] Confirmation time is: {0}'
                                 .format(self.confirm_time))
                    return
            gevent.sleep(1)
#            time.sleep(1)

    def __poll_flows_switches(self, t_start):
        """
        Monitors installed flows into switches of Multinet from the first REST
        request, until the expected number of flows are found or the deadline
        is reached.
        :param t_start: timestamp for beginning of discovery
        :returns: Returns a float number containing the time in which
        total flows were discovered in Multinet switches. Otherwise containing
        -1.0 on failure.
        :rtype: float
        :type t_start: float
        """
        t_discovery_start = time.time()
        previous_discovered_flows = 0
        while True:
            if (time.time() - t_discovery_start) > \
                    self.flows_ds_discovery_deadline:
                logging.info('[NB_generator] [Poll_flows_switches thread] Deadline of {0} seconds passed'
                             .format(self.flows_ds_discovery_deadline))
                self.discover_flows_on_switches_time = -1.0
                logging.info('[NB_generator] [Poll_flows_switches thread] Discovering flows on '
                             'switches FAILED')
                return
            else:
                discovered_flows = self.sbemu.get_flows()
                logging.debug('[NB_generator] [Poll_flows_switches thread] Found {0} flows at '
                              'topology switches'
                              .format(discovered_flows))
                if (discovered_flows - previous_discovered_flows) != 0:
                    t_discovery_start = time.time()
                    previous_discovered_flows = discovered_flows
                if discovered_flows == self.total_flows:
                    time_interval = time.time() - t_start
                    logging.debug('[NB_generator] [Poll_flows_switches thread] expected flows = {0} \n '
                                  'discovered flows = {1}'.
                                  format(self.total_flows, discovered_flows))
                    self.discover_flows_on_switches_time = time_interval
                    logging.info('[NB_generator] [Poll_flows_switches thread] Time to discover flows on '
                                 'switches is: {0}'
                                 .format(self.discover_flows_on_switches_time))
                    return
            gevent.sleep(1)


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
        logging.info('[NB_generator] Creating thread for '
                     'end_to_end_installation_time measurement')
#        monitor_thread_ds = \
#            multiprocessing.Process(target=self.__poll_flows_ds,
#                                    args=(t_start,))
#        monitor_thread_sw = \
#            multiprocessing.Process(target=self.__poll_flows_switches,
#                                    args=(t_start,))
#        monitor_thread_ds_confirm = \
#            multiprocessing.Process(target=self.__poll_flows_ds_confirm)
#        monitor_thread_ds.start()
#        monitor_thread_sw.start()
#        monitor_thread_ds_confirm.start()
#
#        monitor_thread_ds.join()
#        monitor_thread_sw.join()
#        monitor_thread_ds_confirm.join()

        # Monkey patch runtime
        monkey.patch_all()
        monitor_ds = gevent.spawn(self.__poll_flows_ds, t_start)
        monitor_sw = gevent.spawn(self.__poll_flows_switches, t_start)
        monitor_ds_confirm = gevent.spawn(self.__poll_flows_ds_confirm)

        gevent.joinall([monitor_ds, monitor_sw, monitor_ds_confirm])

        time_start = time.time()
        discovered_flows = self.sbemu.get_flows()
        flows_measurement_latency_interval = time.time() - time_start
        logging.info('[NB_generator] Flows measurement latency '
                     'interval: {0} sec. | Discovered flows: {1}'
                     .format(flows_measurement_latency_interval,
                             discovered_flows))
