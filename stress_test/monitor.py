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

    def system_results(self):
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


class Emulator(Monitor):
    def __init__(self, ctrl_base_dir, ctrl_ip, ctrl_sb_port, test_config,
                 test, emulator):
        super(self.__class__, self).__init__(ctrl_base_dir, test_config, test)
        self.emulator = emulator
        self.ctrl_ip = ctrl_ip
        self.ctrl_sb_port = ctrl_sb_port
        self.data_queue = gevent.queue.Queue()
        self.result_queue = gevent.queue.JoinableQueue()
        self.term_success = '__successful_termination__'
        self.term_fail = '__failed_termination__'
        self.total_samples = []

    def monitor_thread_active(self):
        """ Function executed by the monitor thread
        """

        internal_repeat_id = 0
        logging.info('[monitor_thread] Monitor thread started')

        # will hold samples taken in the lifetime of this thread
        results = []
        # Opening connection with controller
        # node to be utilized in the sequel
        while True:
            try:
                # read messages from queue while TERM_SUCCESS has not been sent
                line = self.data_queue.get(block=True, timeout=10000)
                if line == self.term_success:
                    logging.info('[monitor_thread] successful termination '
                                 'string returned. Returning samples and '
                                 'exiting.')
                    self.result_queue.put(results, block=True)
                    self.result_queue.task_done()
                    return
                else:
                    # look for lines containing a substring like e.g.
                    # 'total = 1.2345 per ms'
                    match = re.search(r'total = (.+) per ms', line)
                    if match is not None or line == self.term_fail:
                        results = \
                            self.__monitor_results_active(internal_repeat_id,
                                                          line, results, match)
            except queue.Empty as exept:
                logging.error('[monitor_thread] {0}'.format(str(exept)))
                self.result_queue.put(results, block=True)
                self.result_queue.task_done()
                return

    def monitor_thread_idle(self, boot_start_time,
                            sleep_before_discovery_ms,
                            expected_switches, queuecomm):
        """
        Poll operational DS to discover installed switches
        :param boot_start_time: The time we begin starting topology switches
        :param sleep_before_discovery_ms: amount of time (in milliseconds)
        to sleep before starting polling datastore to discover switches
        :param expected_switches: switches expected to find in the DS
        should discover switches (in milliseconds)
        :param queuecomm: queue for communicating with the main context
        :type boot_start_time: int
        :type sleep_before_discovery_ms: int
        :type expected_switches: int
        :type queuecomm: multiprocessing.Queue
        """

        discovery_deadline = 120
        expected_switches = self.emulator.get_overall_topo_size()
        topology_bootup_time_ms = self.emulator.get_topo_bootup_ms()
        sleep_before_discovery = float(topology_bootup_time_ms) / 1000
        logging.info('[monitor_thread_idle] Monitor thread started')
        t_start = boot_start_time
        logging.info('[monitor_thread_idle] Starting discovery')
        previous_discovered_switches = 0
        discovered_switches = 0
        time.sleep(sleep_before_discovery)
        t_discovery_start = time.time()
        error_code = 0
        max_discovered_switches = 0

        while True:
            if (time.time() - t_discovery_start) > discovery_deadline:
                error_code = 201
                logging.info(
                    '[poll_ds_thread] Deadline of {0} seconds passed, '
                    'discovered {1} switches.'.format(discovery_deadline,
                                                      discovered_switches))
                discovery_time = time.time() - t_start - discovery_deadline
                queuecomm.put((discovery_time, discovered_switches,
                               max_discovered_switches, error_code))

                return 0
            else:
                discovered_switches = self.controller.get_switches()

                if discovered_switches == -1:
                    discovered_switches = previous_discovered_switches
                if discovered_switches > max_discovered_switches:
                    max_discovered_switches = discovered_switches

                if discovered_switches != previous_discovered_switches:
                    t_discovery_start = time.time()
                    previous_discovered_switches = discovered_switches

                if discovered_switches == expected_switches:
                    delta_t = time.time() - t_start
                    logging.info(
                        '[poll_ds_thread] {0} switches found in {1} seconds'.
                        format(discovered_switches, delta_t))

                    queuecomm.put((delta_t, discovered_switches,
                                   max_discovered_switches, error_code))
                    return 0
            time.sleep(1)

    def monitor_run_active(self):

        logging.info('[MTCbench.monitor_run_active] creating and starting'
                     ' monitor and MTCbench threads.')
        # Consumer - producer threads (mtcbench_thread is the producer,
        # monitor_thread is the consumer)
        threads = [gevent.spawn(self.monitor_thread_active()),
                   gevent.spawn(self.mtcbench_thread())]
        gevent.sleep(0)
        samples = self.result_queue.get(block=True)

        self.total_samples = self.total_samples + samples
        gevent.joinall(threads)
        self.result_queue.join()
        gevent.killall(threads)
        return self.total_samples

    def __monitor_results_active(self, internal_repeat_id,
                                 line, results, match):
        statistics = self.system_results()
        statistics['global_sample_id'] = \
            self.test.global_sample_id
        self.global_sample_id += 1
        statistics['repeat_id'] = self.test.repeat_id
        statistics['internal_repeat_id'] = internal_repeat_id
        statistics['cbench_simulated_hosts'] = \
            self.emulator.simulated_hosts
        statistics['cbench_switches'] = \
            self.emulator.switches
        statistics['cbench_threads'] = \
            self.emulator.cbench_threads
        statistics['cbench_switches_per_thread'] = \
            self.emulator.switches_per_thread
        statistics['cbench_thread_creation_delay_ms'] = \
            self.emulator.thread_creation_delay_ms
        statistics['cbench_delay_before_traffic_ms'] = \
            self.emulator.delay_before_traffic_ms
        statistics['controller_statistics_period_ms'] = \
            self.controller.stat_period_ms
        statistics['test_repeats'] = self.test.test_repeats
        statistics['controller_node_ip'] = self.controller.ip
        statistics['controller_port'] = \
            str(self.controller.port)
        statistics['cbench_mode'] = self.emulator.mode
        statistics['cbench_ms_per_test'] = \
            self.emulator.ms_per_test
        statistics['cbench_internal_repeats'] = \
            self.emulator.internal_repeats
        statistics['cbench_warmup'] = self.emulator.warmup
        if line == self.term_fail:
            logging.info('[monitor_thread] returned failed '
                         'termination '
                         'string returning gathered samples '
                         'and exiting.')

            statistics['throughput_responses_sec'] = -1
            results.append(statistics)
            self.result_queue.put(results, block=True)
            return

        if match is not None:
            # extract the numeric portion from the above regex
            statistics['throughput_responses_sec'] = \
                float(match.group(1)) * 1000.0
            results.append(statistics)
        internal_repeat_id += 1
        return results

    def monitor_results_idle(self):
        results = self.system_results()
        results['global_sample_id'] = self.global_sample_id
        self.global_sample_id += 1
        results['cbench_simulated_hosts'] = \
            self.emulator.simulated_hosts
        results['cbench_switches'] = self.emulator.switches
        results['cbench_threads'] = self.emulator.threads
        results['cbench_switches_per_thread'] = \
            self.emulator.switches_per_thread
        results['cbench_thread_creation_delay_ms'] = \
            self.emulator.thread_creation_delay_ms
        results['controller_results_period_ms'] = \
            self.controller.statistics_period_ms
        results['cbench_delay_before_traffic_ms'] = \
            self.emulator.delay_before_traffic_ms
        results['controller_node_ip'] = self.controller.ip
        results['controller_port'] = str(self.controller.port)
        results['cbench_mode'] = self.emulator.mode
        results['cbench_ms_per_test'] = self.emulator.ms_per_test
        results['cbench_internal_repeats'] = \
            self.emulator.internal_repeats

        results['cbench_warmup'] = self.emulator.warmup
        results['bootup_time_secs'] = self.total_samples[0]
        results['discovered_switches'] = self.total_samples[1]
        results['max_discovered_switches'] = self.total_samples[2]
        results['discovered_switches_error_code'] = self.total_samples[-1]
        results['successful_bootup_time'] = \
            self.total_samples[0] if (self.total_samples[-1] == 0) else -1
        self.total_samples.append(results)

    def mtcbench_thread(self):
        """ Function executed by mtcbench thread.
        """
        logging.info('[MTCbench.mtcbench_thread] MTCbench thread started')

        try:
            self.emulator.run(self.ctrl_ip, self.ctrl_sb_port)
            # mtcbench ended, enqueue termination message
            if self.data_queue is not None:
                self.data_queue.put(self.term_success, block=True)
            logging.info('[MTCbench.mtcbench_thread] MTCbench thread ended '
                         'successfully')
        except:
            if self.data_queue is not None:
                self.data_queue.put(self.term_fail, block=True)
            logging.error('[MTCbench.mtcbench_thread] Exception: '
                          'MTCbench_thread exited with error.')
        return


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
                                  .format(self.nbgen.total_flows,
                                          time_interval))
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
        self.exit_flag = False

    def monitor_thread(self, results_queue):
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
        while self.exit_flag.value is False:

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
        self.exit_flag.value = False
#        logging.info('{0} creating idle stability with oftraf '
#                     'monitor thread'.format(test_type))
        monitor_thread = multiprocessing.Process(target=self.monitor_thread,
                                                 args=(result_queue))
        monitor_thread.start()
        res = result_queue.get(block=True)
        self.exit_flag.value = True
        result_queue.close()

#        logging.info('{0} joining monitor thread'.format(test_type))
        monitor_thread.join()
        return res
