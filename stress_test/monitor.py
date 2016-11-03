# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Controller Class- All controller-related functionality is here"""

import gevent
import json
import logging
import multiprocessing
import queue
import re
import subprocess
import time
import util.sysstats


class Monitor:

    def __init__(self, test_config, controller, test_type, test):
        """Create a Monitor. Options from JSON input file
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
        self.test_type = test_type
        self.global_sample_id = 0

    def __sample_stats(self):
        """ Collect runtime statistics
        :returns: experiment statistics in dictionary
        :rtype: dict
        """

        system_statistics = {}
        system_statistics['total_memory_bytes'] = \
            util.sysstats.sys_total_memory_bytes(self.controller.ssh_client)
        system_statistics['controller_cwd'] = \
            util.sysstats.proc_cwd(self.controller.cpid,
                                   self.controller.ssh_client)
        system_statistics['controller_java_xopts'] = \
            util.sysstats.get_java_options(self.controller.cpid,
                                           self.controller.ssh_client)
        system_statistics['timestamp'] = \
            int(subprocess.check_output('date +%s',
                                        shell=True,
                                        universal_newlines=True).strip())
        system_statistics['date'] = \
            subprocess.check_output('date',
                                    shell=True,
                                    universal_newlines=True).strip()
        system_statistics['used_memory_bytes'] = \
            util.sysstats.sys_used_memory_bytes(self.controller.ssh_client)
        system_statistics['free_memory_bytes'] = \
            util.sysstats.sys_free_memory_bytes(self.controller.ssh_client)
        system_statistics['controller_cpu_system_time'] = \
            util.sysstats.proc_cpu_system_time(self.controller.cpid,
                                               self.controller.ssh_client)
        system_statistics['controller_cpu_user_time'] = \
            util.sysstats.proc_cpu_user_time(self.controller.cpid,
                                             self.controller.ssh_client)
        system_statistics['controller_vm_size'] = \
            util.sysstats.proc_vm_size(self.controller.cpid,
                                       self.controller.ssh_client)
        system_statistics['controller_num_fds'] = \
            util.sysstats.proc_num_fds(self.controller.cpid,
                                       self.controller.ssh_client)
        system_statistics['controller_num_threads'] = \
            util.sysstats.proc_num_threads(self.controller.cpid,
                                           self.controller.ssh_client)
        system_statistics['one_minute_load'] = \
            util.sysstats.sys_load_average(self.controller.ssh_client)[0]
        system_statistics['five_minute_load'] = \
            util.sysstats.sys_load_average(self.controller.ssh_client)[1]
        system_statistics['fifteen_minute_load'] = \
            util.sysstats.sys_load_average(self.controller.ssh_client)[2]

        return system_statistics

#    def result_collect_system_stats(self, .....)


class MTCbench(Monitor):
    def __init__(self, ctrl_base_dir, test_config, test, mtcbench):
        super(self.__class__, self).__init__(ctrl_base_dir, test_config, test)
        self.mtcbench = mtcbench
        self.term_success = '__successful_termination__'
        self.term_fail = '__failed_termination__'

    def monitor_thread(self, data_queue, result_queue):
        """ Function executed by the monitor thread
        """

        internal_repeat_id = 0
        logging.info('[monitor_thread] Monitor thread started')

        # will hold samples taken in the lifetime of this thread
        samples = []
        # Opening connection with controller
        # node to be utilized in the sequel
        while True:
            try:
                # read messages from queue while TERM_SUCCESS has not been sent
                line = data_queue.get(block=True, timeout=10000)
                if line == self.term_success:
                    logging.info('[monitor_thread] successful termination '
                                 'string returned. Returning samples and '
                                 'exiting.')
                    result_queue.put(samples, block=True)
                    return
                else:
                    # look for lines containing a substring like e.g.
                    # 'total = 1.2345 per ms'
                    match = re.search(r'total = (.+) per ms', line)
                    if match is not None or line == self.term_fail:
                        statistics = self.__sample_stats()
                        statistics['global_sample_id'] = \
                            self.global_sample_id.value
                        self.global_sample_id.value += 1
                        statistics['repeat_id'] = self.test.repeat_id.value
                        statistics['internal_repeat_id'] = internal_repeat_id
                        statistics['cbench_simulated_hosts'] = \
                            self.mtcbench.simulated_hosts.value
                        statistics['cbench_switches'] = \
                            self.mtcbench.switches.value
                        statistics['cbench_threads'] = \
                            self.mtcbench.cbench_threads.value
                        statistics['cbench_switches_per_thread'] = \
                            self.mtcbench.switches_per_thread.value
                        statistics['cbench_thread_creation_delay_ms'] = \
                            self.mtcbenchthread_creation_delay_ms.value
                        statistics['cbench_delay_before_traffic_ms'] = \
                            self.mtcbench.delay_before_traffic_ms.value
                        statistics['controller_statistics_period_ms'] = \
                            self.controller.stat_period_ms.value
                        statistics['test_repeats'] = self.test.test_repeats
                        statistics['controller_node_ip'] = self.controller.ip
                        statistics['controller_port'] = \
                            str(self.controller.port)
                        statistics['cbench_mode'] = self.mtcbench.mode
                        statistics['cbench_ms_per_test'] = \
                            self.mtcbench.ms_per_test
                        statistics['cbench_internal_repeats'] = \
                            self.mtcbenchinternal_repeats
                        statistics['cbench_warmup'] = self.mtcbench.warmup
                        if line == self.term_fail:
                            logging.info('[monitor_thread] returned failed '
                                         'termination '
                                         'string returning gathered samples '
                                         'and exiting.')

                            statistics['throughput_responses_sec'] = -1
                            samples.append(statistics)
                            result_queue.put(samples, block=True)
                            return

                        if match is not None:

                            # extract the numeric portion from the above regex
                            statistics['throughput_responses_sec'] = \
                                float(match.group(1)) * 1000.0

                            samples.append(statistics)
                        internal_repeat_id += 1

            except queue.Empty as exept:
                logging.error('[monitor_thread] {0}'.format(str(exept)))

    def monitor_run(self):
        total_samples = []
        data_queue = multiprocessing.Queue()
        result_queue = multiprocessing.Queue()

#        logging.info('{0} creating monitor thread'.format(test_type))
        monitor_thread = multiprocessing.Process(
            target=self.monitor_thread, args=(data_queue, result_queue))

#       logging.info('{0} creating cbench thread'.format(test_type))

        # parallel section: starting monitor/cbench threads
        monitor_thread.start()
        samples = result_queue.get(block=True)
        total_samples = total_samples + samples
        monitor_thread.join()
        return total_samples


class NBgen(Monitor):
    def __init__(self, ctrl_base_dir, test_config, test, nbgen):
        super(self.__class__, self).__init__(ctrl_base_dir, test_config, test)
        self.nbgen = nbgen

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
                    self.nbgen.flows_ds_discovery_deadline:
                logging.info('[NB_generator] [Poll_flows thread] Deadline of '
                             '{0} seconds passed'
                             .format(self.nbgen.flows_ds_discovery_deadline))
                self.nbgen.e2e_installation_time = -1.0
                logging.info('[NB_generator] [Poll_flows thread] End to End '
                             'installation time monitor FAILED')
                return
            else:
                new_ssh = self.controller.init_ssh()
                oper_ds_found_flows = self.controller.get_oper_flows(new_ssh)
                logging.debug('[NB_generator] [Poll_flows_ thread] Found {0}'
                              ' flows at inventory'.
                              format(oper_ds_found_flows))
                if (oper_ds_found_flows - previous_discovered_flows) != 0:
                    t_discovery_start = time.time()
                    previous_discovered_flows = oper_ds_found_flows
                if oper_ds_found_flows == self.nbgen.total_flows:
                    time_interval = time.time() - t_start
                    logging.debug('[NB_generator] [Poll_flows thread] '
                                  'Flow-Master {0} flows found in {1} seconds'
                                  .format(self.nbgen.total_flows, time_interval))
                    self.nbgen.e2e_installation_time = time_interval
                    logging.info('[NB_generator] [Poll_flows thread] '
                                 'End to End installation time is: {0}'
                                 .format(self.nbgen.e2e_installation_time))
                    return
            gevent.sleep(1)

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
                    self.nbgen.flows_ds_discovery_deadline:
                logging.info('[NB_generator] [Poll_flows_confirm thread] '
                             ' Deadline of {0} seconds passed'
                             .format(self.flows_ds_discovery_deadline))
                self.nbgen.confirm_time = -1.0
                logging.info('[NB_generator] [Poll_flows_confirm thread] '
                             'Confirmation time monitoring FAILED')
                return
            else:
                new_ssh = self.controller.init_ssh()
                oper_ds_found_flows = self.controller.get_oper_flows(new_ssh)
                logging.debug('[NB_generator] [Poll_flows_confirm thread] '
                              'Found {0} flows at inventory'
                              .format(oper_ds_found_flows))
                if (oper_ds_found_flows - previous_discovered_flows) != 0:
                    t_discovery_start = time.time()
                    previous_discovered_flows = oper_ds_found_flows
                if oper_ds_found_flows == self.nbgen.total_flows:
                    time_interval = time.time() - t_start
                    logging.debug('[NB_generator] [Poll_flows_confirm thread] '
                                  'Flow-Master {0} flows found in {1} seconds'
                                  .format(self.nbgen.total_flows,
                                          time_interval))
                    self.nbgen.confirm_time = time_interval
                    logging.info('[NB_generator] [Poll_flows_confirm thread] '
                                 'Confirmation time is: {0}'
                                 .format(self.nbgen.confirm_time))
                    return
            gevent.sleep(1)

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
                    self.nbgen.flows_ds_discovery_deadline:
                logging.info('[NB_generator] [Poll_flows_switches thread] '
                             'Deadline of {0} seconds passed'
                             .format(self.flows_ds_discovery_deadline))
                self.nbgen.discover_flows_on_switches_time = -1.0
                logging.info('[NB_generator] [Poll_flows_switches thread] '
                             'Discovering flows on switches FAILED')
                return
            else:
                new_ssh = self.sbemu.init_ssh()
                discovered_flows = self.sbemu.get_flows(new_ssh)
                logging.debug('[NB_generator] [Poll_flows_switches thread] '
                              'Found {0} flows at topology switches'
                              .format(discovered_flows))
                if (discovered_flows - previous_discovered_flows) != 0:
                    t_discovery_start = time.time()
                    previous_discovered_flows = discovered_flows
                if discovered_flows == self.nbgen.total_flows:
                    time_interval = time.time() - t_start
                    logging.debug('[NB_generator] [Poll_flows_switches thread]'
                                  ' expected flows = {0} \n '
                                  'discovered flows = {1}'
                                  .format(self.nbgen.total_flows,
                                          discovered_flows))
                    self.discover_flows_on_switches_time = time_interval
                    logging.info('[NB_generator] [Poll_flows_switches thread] '
                                 'Time to discover flows on switches is: {0}'
                                 .format(self.nbgen.discover_flows_on_switches_time))
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
        logging.info('[NB_generator] Start polling measurements')

        monitor_ds = gevent.spawn(self.__poll_flows_ds, t_start)
        monitor_sw = gevent.spawn(self.__poll_flows_switches, t_start)
        monitor_ds_confirm = gevent.spawn(self.__poll_flows_ds_confirm)
        gevent.joinall([monitor_ds, monitor_sw, monitor_ds_confirm])

        time_start = time.time()
        discovered_flows = self.sbemu.get_flows()
        flow_measurement_latency_interval = time.time() - time_start
        logging.info('[NB_generator] Flows measurement latency '
                     'interval: {0} sec. | Discovered flows: {1}'
                     .format(flow_measurement_latency_interval,
                             discovered_flows))


class Oftraf(Monitor):

    def __init__(self, ctrl_base_dir, test_config, test, oftraf):
        super(self.__class__, self).__init__(ctrl_base_dir, test_config, test)
        self.oftraf = oftraf

    def monitor_thread(self, results_queue, exit_flag):
        """Function executed inside a thread and returns the output in json
        format, of openflow packets counts

        :param oftraf_interval_ms: interval in milliseconds, after which we
        want to get an oftraf measurement
        :param oftraf_rest_server: a named tuple python collection,
        containing the IP address and the port number of oftraf rest server
        :param results_queue: the multiprocessing Queue used for the
        communication between the NSTAT master thread and oftraf thread.
        In this Queue we return the result
        :type oftraf_interval_ms: int
        :type oftraf_rest_server: collections.namedtuple<str,int>
        :type results_queue: multiprocessing.Queue
        """
        while exit_flag.value is False:

            oftraf_interval_sec = self.oftraf.oftraf_interval_ms / 1000
            logging.info('[oftraf_monitor_thread] Waiting for {0} seconds.'.
                         format(oftraf_interval_sec))
            time.sleep(oftraf_interval_sec)
            logging.info('[oftraf_monitor_thread] '
                         'get throughput of controller')
            response_data = \
                json.loads(self.oftraf.oftraf_get_of_counts())
            tcp_out_traffic = tuple(response_data['TCP_OF_out_counts'])
            tcp_in_traffic = tuple(response_data['TCP_OF_in_counts'])
            out_traffic = tuple(response_data['OF_out_counts'])
            in_traffic = tuple(response_data['OF_in_counts'])
            results = {'of_out_traffic': out_traffic,
                       'of_in_traffic': in_traffic,
                       'tcp_of_out_traffic': tcp_out_traffic,
                       'tcp_of_in_traffic': tcp_in_traffic}
            results_queue.put(results, block=True)
        return

    def monitor_run(self):
        result_queue = multiprocessing.Queue(maxsize=1)

        # Parallel section
        exit_flag = False
#        logging.info('{0} creating idle stability with oftraf '
#                     'monitor thread'.format(test_type))
        monitor_thread = multiprocessing.Process(target=self.monitor_thread,
                                                 args=(result_queue,
                                                       exit_flag))

        monitor_thread.start()
        res = result_queue.get(block=True)
        exit_flag.value = True
        result_queue.close()

#        logging.info('{0} joining monitor thread'.format(test_type))
        monitor_thread.join()
        return res
