# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Controller Class- All controller-related functionality is here"""

import gevent
import gevent.queue
import json
import logging
import re
import queue
import subprocess
import time
import util.sysstats


class Monitor:

    def __init__(self, controller):
        """Create a Monitor. Options from JSON input file
        :param nb_gen_base_dir: emulator base directory
        :param controller: object of the Controller class
        :param sbemu: object of the SBEmu subclass
        :type nb_gen_base_dir: str
        :type controller: object
        :type sbemu: object
        """
        self.controller = controller
        self.global_sample_id = 0
        self.repeat_id = 0
        self.test_repeats = 0

    def system_results(self):
        """ Collect runtime statistics
        :returns: experiment statistics in dictionary
        :rtype: dict
        """

        system_statistics = {}
        system_statistics['total_memory_bytes'] = \
            util.sysstats.sys_total_memory_bytes(self.controller._ssh_conn)
        system_statistics['controller_cwd'] = \
            util.sysstats.proc_cwd(self.controller.pid,
                                   self.controller._ssh_conn)
        system_statistics['controller_java_xopts'] = \
            util.sysstats.get_java_options(self.controller.pid,
                                           self.controller._ssh_conn)
        system_statistics['timestamp'] = \
            int(subprocess.check_output('date +%s',
                                        shell=True,
                                        universal_newlines=True).strip())
        system_statistics['date'] = \
            subprocess.check_output('date',
                                    shell=True,
                                    universal_newlines=True).strip()
        system_statistics['used_memory_bytes'] = \
            util.sysstats.sys_used_memory_bytes(self.controller._ssh_conn)
        system_statistics['free_memory_bytes'] = \
            util.sysstats.sys_free_memory_bytes(self.controller._ssh_conn)
        system_statistics['controller_cpu_system_time'] = \
            util.sysstats.proc_cpu_system_time(self.controller.pid,
                                               self.controller._ssh_conn)
        system_statistics['controller_cpu_user_time'] = \
            util.sysstats.proc_cpu_user_time(self.controller.pid,
                                             self.controller._ssh_conn)
        system_statistics['controller_vm_size'] = \
            util.sysstats.proc_vm_size(self.controller.pid,
                                       self.controller._ssh_conn)
        system_statistics['controller_num_fds'] = \
            util.sysstats.proc_num_fds(self.controller.pid,
                                       self.controller._ssh_conn)
        system_statistics['controller_num_threads'] = \
            util.sysstats.proc_num_threads(self.controller.pid,
                                           self.controller._ssh_conn)
        system_statistics['one_minute_load'] = \
            util.sysstats.sys_load_average(self.controller._ssh_conn)[0]
        system_statistics['five_minute_load'] = \
            util.sysstats.sys_load_average(self.controller._ssh_conn)[1]
        system_statistics['fifteen_minute_load'] = \
            util.sysstats.sys_load_average(self.controller._ssh_conn)[2]
        return system_statistics


class Oftraf:

    def __init__(self, controller, oftraf):
        self.oftraf = oftraf
        self.controller = controller
        self.exit_flag = False
        self.results_queue = gevent.queue.Queue(maxsize=1)

    def of_monitor_thread(self):
        """Function executed inside a thread and returns the output in json
        format, of openflow packets counts
        """
        try:
            while self.exit_flag is False:
                oftraf_interval_sec = self.oftraf.interval_ms / 1000
                logging.info('[oftraf_monitor_thread] Waiting for {0} seconds.'
                             .format(oftraf_interval_sec))
                gevent.sleep(oftraf_interval_sec)
                logging.info('[oftraf_monitor_thread] '
                             'get throughput of controller')
                response_data = \
                    json.loads(self.oftraf.oftraf_get_of_counts())
                print('*******response_data from OFTRAF***************')
                print('*******response_data from OFTRAF***************')
                print(response_data)
                tcp_out_traffic = tuple(response_data['TCP_OF_out_counts'])
                tcp_in_traffic = tuple(response_data['TCP_OF_in_counts'])
                out_traffic = tuple(response_data['OF_out_counts'])
                in_traffic = tuple(response_data['OF_in_counts'])
                results = {'of_out_traffic': out_traffic,
                           'of_in_traffic': in_traffic,
                           'tcp_of_out_traffic': tcp_out_traffic,
                           'tcp_of_in_traffic': tcp_in_traffic}
                self.exit_flag = True
        except:
            logging.error('[oftraf.monitor_thread] Error monitor thread '
                          'failed.')
            results = {'of_out_traffic': (0, 0),
                       'of_in_traffic': (0, 0),
                       'tcp_of_out_traffic': (0, 0),
                       'tcp_of_in_traffic': (0, 0)}
            exit()
        self.results_queue.put(results)

    def monitor_run_oftraf(self):

        # Parallel section
        self.exit_flag = False
        monitor_thread = gevent.spawn(self.of_monitor_thread)
        res = self.results_queue.get(block=True)
        gevent.joinall([monitor_thread])
        gevent.killall([monitor_thread])
        return res


class Mtcbench(Monitor):
    def __init__(self, controller, emulator):
        super(self.__class__, self).__init__(controller)
        self.emulator = emulator
        self.result_queue = gevent.queue.Queue()
        self.term_success = '__successful_termination__'
        self.term_fail = '__failed_termination__'
        self.data_queue = gevent.queue.Queue()

    def monitor_results_active(self):
        results = self.system_results()
        results['global_sample_id'] = \
            self.global_sample_id
        self.global_sample_id += 1
        results['repeat_id'] = self.repeat_id

        results['cbench_simulated_hosts'] = \
            self.emulator.simulated_hosts
        results['cbench_switches'] = \
            self.emulator.get_overall_topo_size()
        results['cbench_threads'] = \
            self.emulator.threads
        results['cbench_switches_per_thread'] = \
            self.emulator.switches_per_thread
        results['cbench_thread_creation_delay_ms'] = \
            self.emulator.thread_creation_delay_ms
        results['cbench_delay_before_traffic_ms'] = \
            self.emulator.delay_before_traffic_ms
        results['controller_statistics_period_ms'] = \
            self.controller.stat_period_ms
        results['test_repeats'] = self.test_repeats
        results['controller_node_ip'] = self.controller.ip
        results['controller_port'] = \
            str(self.controller.of_port)
        results['cbench_mode'] = self.emulator.mode
        results['cbench_ms_per_test'] = \
            self.emulator.ms_per_test
        results['cbench_internal_repeats'] = \
            self.emulator.internal_repeats
        results['cbench_warmup'] = self.emulator.warmup
        return results

    def monitor_results_idle(self):
        results = self.system_results()
        results['global_sample_id'] = self.global_sample_id
        self.global_sample_id += 1
        results['cbench_simulated_hosts'] = \
            self.emulator.simulated_hosts
        results['cbench_switches'] = self.emulator.get_overall_topo_size()
        results['cbench_threads'] = self.emulator.threads
        results['cbench_switches_per_thread'] = \
            self.emulator.switches_per_thread
        results['cbench_thread_creation_delay_ms'] = \
            self.emulator.thread_creation_delay_ms
        results['controller_statistics_period_ms'] = \
            self.controller.stat_period_ms
        results['cbench_delay_before_traffic_ms'] = \
            self.emulator.delay_before_traffic_ms
        results['controller_node_ip'] = self.controller.ip
        results['controller_port'] = self.controller.of_port
        results['cbench_mode'] = self.emulator.mode
        results['cbench_ms_per_test'] = self.emulator.ms_per_test
        results['cbench_internal_repeats'] = \
            self.emulator.internal_repeats
        results['cbench_warmup'] = self.emulator.warmup
        return results

    def monitor_thread_idle(self, boot_start_time):
        """
        This monitor function is used from idle tests.
        Poll operational DS to discover installed switches.
        It is used for idle tests from mtcbench and multinet emulators.
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
                    '[monitor_thread_idle] Deadline of {0} seconds passed, '
                    'discovered {1} switches.'.format(discovery_deadline,
                                                      discovered_switches))
                discovery_time = time.time() - t_start - discovery_deadline
                results = self.monitor_results_idle()
                results['bootup_time_secs'] = discovery_time
                results['discovered_switches'] = discovered_switches
                results['max_discovered_switches'] = max_discovered_switches
                results['discovered_switches_error_code'] = error_code
                results['successful_bootup_time'] = -1
                self.result_queue.put([results])
                return 0
            else:
                new_ssh = self.controller.init_ssh()
                discovered_switches = self.controller.get_oper_switches(new_ssh)
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
                        '[monitor_thread_idle] {0} switches found in '
                        '{1} seconds'.
                        format(discovered_switches, delta_t))
                    results = self.monitor_results_idle()
                    results['bootup_time_secs'] = delta_t
                    results['discovered_switches'] = discovered_switches
                    results['max_discovered_switches'] = \
                        max_discovered_switches
                    results['discovered_switches_error_code'] = error_code
                    results['successful_bootup_time'] = delta_t
                    self.result_queue.put([results])
                    return 0
            gevent.sleep(1)

    def monitor_thread_active(self):
        """
        This monitor function is used by active tests
        Function executed by the monitor thread
        It is used for active tests.
        """

        internal_repeat_id = 0
        logging.info('[monitor_thread_active] monitor thread started')

        # will hold samples taken in the lifetime of this thread
        test_samples = []
        # Opening connection with controller
        # node to be utilized in the sequel
        while True:
            try:
                # read messages from queue while TERM_SUCCESS has not been sent
                line = self.data_queue.get(block=True)
                if line == self.term_success:
                    logging.info('[monitor_thread_active] successful '
                                 'termination string returned. Returning '
                                 'samples and exiting.')
                    self.result_queue.put(test_samples)
                    return
                else:
                    # look for lines containing a substring like e.g.
                    # 'total = 1.2345 per ms'
                    match = re.search(r'total = (.+) per ms', line)
                    if match is not None or line == self.term_fail:
                        results = self.monitor_results_active()
                        if line == self.term_fail:
                            logging.info('[monitor_thread] returned failed '
                                         'termination '
                                         'string returning gathered samples '
                                         'and exiting.')
                            results['throughput_responses_sec'] = -1
                            results['internal_repeat_id'] = internal_repeat_id
                            test_samples.append(results)
                            self.result_queue.put(test_samples)
                            return
                        if match is not None:
                            # extract the numeric portion from the above regex
                            results['throughput_responses_sec'] = \
                                float(match.group(1)) * 1000.0
                        results['internal_repeat_id'] = internal_repeat_id
                        test_samples.append(results)
                        internal_repeat_id += 1
            except queue.Empty as exept:
                logging.error('[monitor_thread_active] {0}'.format(str(exept)))
                self.result_queue.put(test_samples)
                return
            gevent.sleep(0.5)

    def monitor_run(self, boot_start_time=None):

        logging.info('[MTCbench.monitor_run] creating and starting'
                     ' monitor and MTCbench threads.')
        # Consumer - producer threads (mtcbench_thread is the producer,
        # monitor_thread is the consumer)
        threads = []
        if boot_start_time is None:
            logging.info('[MTCbench.monitor_run] active test monitor is '
                         'running')
            monitor_thread = gevent.spawn(self.monitor_thread_active)
            threads.append(monitor_thread)
            mtcbench_thread = gevent.spawn(self.mtcbench_thread,
                                           True, self.data_queue)
            threads.append(mtcbench_thread)
        else:
            logging.info('[MTCbench.monitor_run] idle test monitor is running')
            self.mtcbench_thread(False, None)
            monitor_thread = \
                gevent.spawn(self.monitor_thread_idle, boot_start_time)
            threads.append(monitor_thread)
        gevent.joinall(threads)
        samples = self.result_queue.get()
        gevent.killall(threads)
        return samples

    def mtcbench_thread(self, block_flag=True, data_queue=None):
        """ Function executed by mtcbench thread.
        """
        logging.info('[MTCbench.mtcbench_thread] MTCbench thread started')
        try:
            self.emulator.run(self.controller.ip, self.controller.of_port,
                              '[MTCbench.mtcbench_thread]', data_queue,
                              False, block_flag, False)
            # mtcbench ended, enqueue termination message
            if data_queue is not None:
                data_queue.put_nowait(self.term_success)
            logging.info('[MTCbench.mtcbench_thread] MTCbench thread ended '
                         'successfully')
        except:
            if data_queue is not None:
                data_queue.put_nowait(self.term_fail)
            logging.error('[MTCbench.mtcbench_thread] Exception: '
                          'MTCbench_thread exited with error.')
        return 0


class Multinet(Monitor):
    def __init__(self, controller, oftraf, emulator):
        Monitor.__init__(self, controller)
        # Oftraf.__init__(self, controller, oftraf)
        self.oftraf_node = oftraf
        self.emulator = emulator
        self.result_queue = gevent.queue.Queue()

    def monitor_run(self, reference_results=None,
                    sample_id=None,
                    boot_start_time=None):

        logging.info('[Multinet.monitor_run] creating and starting'
                     ' monitoring of Multinet worker events.')
        if boot_start_time is None and sample_id is None:
            logging.info('[Multinet.monitor_run] Active test monitor is '
                         'running')
            monitor_thread = gevent.spawn(self.monitor_thread_active)
        elif self.oftraf_node is None:
            logging.info('[Multinet.monitor_run] Idle scalability test '
                         'monitor is running')
            monitor_thread = \
                gevent.spawn(self.monitor_thread_idle_scalability,
                             boot_start_time)
        else:
            logging.info('[Multinet.monitor_run] Idle test stability '
                         'monitor is running')
            monitor_thread = \
                gevent.spawn(self.monitor_thread_idle_stability,
                             reference_results,
                             sample_id)
            # self.emulator.start_topos()
        gevent.joinall([monitor_thread])
        total_results = self.result_queue.get()
        gevent.killall([monitor_thread])

        if boot_start_time is None and sample_id is None:
            return total_results
        elif self.oftraf_node is None:
            return total_results
        else:
            return (total_results["current_sample"],
                    total_results["previous_sample"])

    def monitor_thread_idle_scalability(self, boot_start_time):
        """
        This monitor function is used from idle tests.
        Poll operational DS to discover installed switches.
        It is used for idle tests from mtcbench and multinet emulators.
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
            results = self.system_results()
            results['global_sample_id'] = self.global_sample_id
            self.global_sample_id += 1
            results['multinet_workers'] = len(self.emulator.workers_ips)
            results['multinet_worker_topo_size'] = self.emulator.topo_size
            results['multinet_topology_type'] = self.emulator.topo_type
            results['multinet_hosts_per_switch'] = \
                self.emulator.topo_hosts_per_switch
            results['multinet_group_size'] = self.emulator.topo_group_size
            results['multinet_group_delay_ms'] = \
                self.emulator.topo_group_delay_ms
            results['controller_statistics_period_ms'] = \
                self.controller.stat_period_ms
            results['controller_node_ip'] = self.controller.ip
            results['controller_port'] = str(self.controller.of_port)

            if (time.time() - t_discovery_start) > discovery_deadline:
                error_code = 201
                logging.info(
                    '[monitor_thread_idle] Deadline of {0} seconds passed, '
                    'discovered {1} switches.'.format(discovery_deadline,
                                                      discovered_switches))
                discovery_time = time.time() - t_start - discovery_deadline
                results = self.monitor_results_idle()
                results['multinet_size'] = topology_bootup_time_ms
                results['bootup_time_secs'] = discovery_time
                results['discovered_switches'] = discovered_switches
                results['max_discovered_switches'] = max_discovered_switches
                results['discovered_switches_error_code'] = error_code
                results['successful_bootup_time'] = -1
                self.result_queue.put([results])
                return 0
            else:
                new_ssh = self.controller.init_ssh()
                discovered_switches = \
                    self.controller.get_oper_switches(new_ssh)
                logging.info('Discovered switches: ='
                             .format(discovered_switches))

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
                        '[monitor_thread_idle] {0} switches found in '
                        '{1} seconds'.
                        format(discovered_switches, delta_t))
                    results = self.monitor_results_idle()
                    results['multinet_size'] = topology_bootup_time_ms
                    results['bootup_time_secs'] = delta_t
                    results['discovered_switches'] = discovered_switches
                    results['max_discovered_switches'] = \
                        max_discovered_switches
                    results['discovered_switches_error_code'] = error_code
                    results['successful_bootup_time'] = delta_t
                    self.result_queue.put([results])
                    return 0
            gevent.sleep(1)

    def monitor_thread_idle_stability(self, reference_results, sample_id):
        """
        """
        oftraf_mon = Oftraf(self.controller, self.oftraf_node)
        oftraf_monitor_results = oftraf_mon.monitor_run_oftraf()
        results = self.system_results()
        results['global_sample_id'] = self.global_sample_id
        self.global_sample_id += 1
        results['multinet_workers'] = len(self.emulator.workers_ips)
        results['multinet_size'] = \
            self.emulator.topo_size * len(self.emulator.workers_ips)
        results['multinet_worker_topo_size'] = self.emulator.topo_size
        results['multinet_topology_type'] = self.emulator.topo_type
        results['multinet_hosts_per_switch'] = \
            self.emulator.topo_hosts_per_switch
        results['multinet_group_size'] = self.emulator.topo_group_size
        results['multinet_group_delay_ms'] = self.emulator.topo_group_delay_ms
        results['controller_statistics_period_ms'] = \
            self.controller.stat_period_ms
        results['controller_node_ip'] = self.controller.ip
        results['controller_port'] = str(self.controller.of_port)

        traffic_gen_ms = float(self.oftraf_node.interval_ms) / 1000
        results['of_out_packets_per_sec'] = \
            (abs(float(oftraf_monitor_results['of_out_traffic'][0])) -
             reference_results['of_out_traffic'][0]) / traffic_gen_ms
        results['of_out_bytes_per_sec'] = \
            (abs(float(oftraf_monitor_results['of_out_traffic'][1])) -
             reference_results['of_out_traffic'][1]) / traffic_gen_ms
        results['of_in_packets_per_sec'] = \
            (abs(float(oftraf_monitor_results['of_in_traffic'][0])) -
             reference_results['of_in_traffic'][0]) / traffic_gen_ms
        results['of_in_bytes_per_sec'] = \
            (abs(float(oftraf_monitor_results['of_in_traffic'][1])) -
             reference_results['of_in_traffic'][1]) / traffic_gen_ms
        results['tcp_of_out_packets_per_sec'] = \
            (abs(float(oftraf_monitor_results['tcp_of_out_traffic'][0])) -
             reference_results['tcp_of_out_traffic'][0]) / traffic_gen_ms
        results['tcp_of_out_bytes_per_sec'] = \
            (abs(float(oftraf_monitor_results['tcp_of_out_traffic'][1])) -
             reference_results['tcp_of_out_traffic'][1]) / traffic_gen_ms
        results['tcp_of_in_packets_per_sec'] = \
            (abs(float(oftraf_monitor_results['tcp_of_in_traffic'][0])) -
             reference_results['tcp_of_in_traffic'][0]) / traffic_gen_ms
        results['tcp_of_in_bytes_per_sec'] = \
            (abs(float(oftraf_monitor_results['tcp_of_in_traffic'][1])) -
             reference_results['tcp_of_in_traffic'][1]) / traffic_gen_ms
        results['sample_id'] = sample_id

        self.result_queue.put({"current_sample": results,
                               "previous_sample": reference_results})

        reference_results = oftraf_monitor_results

        print('*******RESULTS FROM IDLE STAB MONITOR f************')
        print('*******RESULTS FROM IDLE STAB MONITOR f************')
        print(results)

        print('*******reference_results FROM IDLE STAB MONITOR f************')
        print('*******reference_results FROM IDLE STAB MONITOR f************')
        print(reference_results)

        self.result_queue.put({"current_sample": results,
                               "previous_sample": reference_results})
        return

    def monitor_thread_active(self):
        """ Function executed by multinet thread.
            It calls monitor_thread() method of Oftraf Class
        """
        oftraf_mon = Oftraf(self.controller, self.oftraf_node)
        oftraf_monitor_results = oftraf_mon.monitor_run_oftraf()
        results = self.system_results()
        results['global_sample_id'] = self.global_sample_id
        self.global_sample_id += 1
        results['multinet_workers'] = len(self.emulator.workers_ips)
        results['multinet_size'] = \
            self.emulator.topo_size * len(self.emulator.workers_ips)
        results['multinet_worker_topo_size'] = self.emulator.topo_size
        results['multinet_topology_type'] = self.emulator.topo_type
        results['multinet_hosts_per_switch'] = \
            self.emulator.topo_hosts_per_switch
        results['multinet_group_size'] = self.emulator.topo_group_size
        results['multinet_group_delay_ms'] = self.emulator.topo_group_delay_ms
        results['controller_statistics_period_ms'] = \
            self.controller.stat_period_ms
        results['controller_node_ip'] = self.controller.ip
        results['controller_port'] = str(self.controller.of_port)
        results['interpacket_delay_ms'] = self.emulator.interpacket_delay_ms
        results['traffic_generation_duration_ms'] = \
            self.emulator.traffic_gen_duration_ms
        traffic_gen_ms = float(self.emulator.traffic_gen_duration_ms) / 1000
        results['of_out_packets_per_sec'] = \
            float(oftraf_monitor_results['of_out_traffic'][0]) / traffic_gen_ms
        results['of_out_bytes_per_sec'] = \
            float(oftraf_monitor_results['of_out_traffic'][1]) / traffic_gen_ms
        results['of_in_packets_per_sec'] = \
            float(oftraf_monitor_results['of_in_traffic'][0]) / traffic_gen_ms
        results['of_in_bytes_per_sec'] = \
            float(oftraf_monitor_results['of_in_traffic'][1]) / traffic_gen_ms
        results['tcp_of_out_packets_per_sec'] = \
            float(oftraf_monitor_results['tcp_of_out_traffic'][0]) / traffic_gen_ms
        results['tcp_of_out_bytes_per_sec'] = \
            float(oftraf_monitor_results['tcp_of_out_traffic'][1]) / traffic_gen_ms
        results['tcp_of_in_packets_per_sec'] = \
            float(oftraf_monitor_results['tcp_of_in_traffic'][0]) / traffic_gen_ms
        results['tcp_of_in_bytes_per_sec'] = \
            float(oftraf_monitor_results['tcp_of_in_traffic'][1]) / traffic_gen_ms
        self.result_queue.put([results])
        return 0


class NBgen(Monitor):
    def __init__(self, controller, nbgen, sbemu):
        Monitor.__init__(self, controller)
        self.nbgen_queue = gevent.queue.Queue()
        self.nbgen = nbgen
        self.sbemu = sbemu
        #self.test = test

    def __poll_flows_ds(self, t_start, expected_flows):
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
                self.nbgen_queue.put({'end_to_end_flows_operation_time': -1.0},
                                     block=True)
                logging.info('[NB_generator] [Poll_flows thread] End to End '
                             'installation time monitor FAILED')
                return
            else:
                new_ssh = self.controller.init_ssh()
                oper_ds_found_flows = self.controller.get_oper_flows(new_ssh)
                logging.debug('[NB_generator] [Poll_flows thread] Found {0}'
                              ' flows at inventory'.
                              format(oper_ds_found_flows))
                if (oper_ds_found_flows - previous_discovered_flows) != 0:
                    t_discovery_start = time.time()
                    previous_discovered_flows = oper_ds_found_flows
                if oper_ds_found_flows == expected_flows:
                    time_interval = time.time() - t_start
                    logging.debug('[NB_generator] [Poll_flows thread] '
                                  'Flow-Master {0} flows found in {1} seconds'
                                  .format(expected_flows, time_interval))
                    self.nbgen.e2e_installation_time = time_interval
                    self.nbgen_queue.put(
                        {'end_to_end_flows_operation_time': time_interval},
                        block=True)
                    logging.info('[NB_generator] [Poll_flows thread] '
                                 'End to End installation time is: {0}'
                                 .format(self.nbgen.e2e_installation_time))
                    return
            gevent.sleep(1)

    def __poll_flows_ds_confirm(self, expected_flows):
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
                self.nbgen_queue.put({'confirm_time': -1.0}, block=True)
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
                if oper_ds_found_flows == expected_flows:
                    time_interval = time.time() - t_start
                    logging.debug('[NB_generator] [Poll_flows_confirm thread] '
                                  'Flow-Master {0} flows found in {1} seconds'
                                  .format(expected_flows,
                                          time_interval))
                    self.nbgen.confirm_time = time_interval
                    self.nbgen_queue.put({'confirm_time': time_interval},
                                         block=True)
                    logging.info('[NB_generator] [Poll_flows_confirm thread] '
                                 'Confirmation time is: {0}'
                                 .format(self.nbgen.confirm_time))
                    return
            gevent.sleep(1)

    def __poll_flows_switches(self, t_start, expected_flows):
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
                self.nbgen_queue.put({'switch_operation_time': -1.0},
                                     block=True)
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
                if discovered_flows == expected_flows:
                    time_interval = time.time() - t_start
                    logging.debug('[NB_generator] [Poll_flows_switches thread]'
                                  ' expected flows = {0} \n '
                                  'discovered flows = {1}'
                                  .format(expected_flows, discovered_flows))
                    self.discover_flows_on_switches_time = time_interval
                    self.nbgen_queue.put(
                        {'switch_operation_time': time_interval}, block=True)
                    logging.info('[NB_generator] [Poll_flows_switches thread] '
                                 'Time to discover flows on switches is: {0}'
                                 .format(self.nbgen.discover_flows_on_switches_time))
                    return
            gevent.sleep(1)

    def __controller_time(self, t_start):
        """
        Monitors the time for all add REST requests to be sent and their
        response to be received.
        :param t_start: timestamp for beginning of discovery
        :returns: Returns a float number containing the time in which
        total flows were discovered in Multinet switches. Otherwise containing
        -1.0 on failure.
        :rtype: float
        :type t_start: float
        """
        controller_time = time.time() - t_start
        return controller_time

    def monitor_threads_run(self, t_start, total_failed_flows,
                            expected_flows,
                            flow_delete_flag):
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
        monitor_ds = gevent.spawn(self.__poll_flows_ds, t_start, expected_flows)
        monitor_sw = gevent.spawn(self.__poll_flows_switches, t_start, expected_flows)
        monitor_ds_confirm = gevent.spawn(self.__poll_flows_ds_confirm, expected_flows)
        gevent.joinall([monitor_ds, monitor_sw, monitor_ds_confirm])
        gevent.killall([monitor_ds, monitor_sw, monitor_ds_confirm])

        time_start = time.time()
        controller_time = self.__controller_time(t_start)
        discovered_flows = self.sbemu.get_flows()
        flow_measurement_latency_interval = time.time() - time_start
        logging.info('[NB_generator] Flows measurement latency '
                     'interval: {0} sec. | Discovered flows: {1}'
                     .format(flow_measurement_latency_interval,
                             discovered_flows))

        results_thread = {}
        results = {}

        while not self.nbgen_queue.empty():
            results_thread.update(self.nbgen_queue.get())

        if flow_delete_flag is False:
            results = self.monitor_results_add(controller_time,
                                               results_thread,
                                               total_failed_flows)
        else:
            results = self.monitor_results_del(controller_time,
                                               results_thread,
                                               total_failed_flows)
        return results

    def monitor_results_add(self, add_controller_time,
                        results_thread, total_failed_flows):

        results = self.system_results()
        results['global_sample_id'] = self.global_sample_id
        #self.global_sample_id += 1
        results['multinet_workers'] = len(self.sbemu.workers_ips)
        results['multinet_size'] = \
            self.sbemu.topo_size * len(self.sbemu.workers_ips)
        results['multinet_worker_topo_size'] = self.sbemu.topo_size
        results['multinet_topology_type'] = self.sbemu.topo_type
        results['multinet_hosts_per_switch'] = \
            self.sbemu.topo_hosts_per_switch
        results['multinet_group_size'] = self.sbemu.topo_group_size
        results['multinet_group_delay_ms'] = self.sbemu.topo_group_delay_ms
        results['controller_statistics_period_ms'] = \
            self.controller.stat_period_ms
        results['controller_node_ip'] = self.controller.ip
        results['controller_port'] = str(self.controller.of_port)
        results['interpacket_delay_ms'] = self.sbemu.interpacket_delay_ms
        results['traffic_generation_duration_ms'] = \
            self.sbemu.traffic_gen_duration_ms
        results['flow_operation_delay_ms'] = \
            self.nbgen.flow_operations_delay_ms
        results['flow_workers'] = \
            self.nbgen.flow_workers

        # Flow scalability tests metrics
        # ------------------------------------------------------------------
        # Add controller time: Time for all ADD REST requests to be sent
        #                      and their response to be received
        results['add_controller_time'] = add_controller_time
        results['add_controller_rate'] = \
            float(self.nbgen.total_flows) / add_controller_time

        # End-to-end-installation-time:

        results['end_to_end_installation_time'] = \
            results_thread['end_to_end_flows_operation_time']
        if results_thread['end_to_end_flows_operation_time'] != -1:
            results['end_to_end_installation_rate'] = \
                float(self.nbgen.total_flows) / results_thread['end_to_end_flows_operation_time']
        else:
            results['end_to_end_installation_rate'] = -1

        # Add switch time: Time from the FIRST REST request until ALL flows
        #                  are present in the network

        results['add_switch_time'] = results_thread['switch_operation_time']
        if results_thread['switch_operation_time'] != -1:
            results['add_switch_rate'] = \
                float(self.nbgen.total_flows) / results_thread['switch_operation_time']
        else:
            results['add_switch_rate'] = -1

        results['add_confirm_time'] = results_thread['confirm_time']
        if results_thread['confirm_time'] != -1:
            results_thread['confirm_time'] = \
                float(self.nbgen.total_flows) / results_thread['confirm_time']
        else:
            results['add_confirm_rate'] = -1

        results['total_failed_flows_operations'] = total_failed_flows
        return results

    def monitor_results_del(self, controller_time,
                                     results_thread,
                                     total_failed_flows):

        # Remove controller time: Time for all delete REST
        #                          requests to be sent and their response to
        #                          be received
        #results = {}
        results = self.system_results()
        results['remove_controller_time'] = controller_time
        results['remove_controller_rate'] = \
            float(self.nbgen.total_flows) / controller_time

        # end_to_end_remove_time: The time period started after the last
        #                   flow was configured, until we receive confirmation
        #                   all flows were removed.
        results['end_to_end_remove_time'] = \
            results_thread['end_to_end_flows_operation_time']
        results['end_to_end_remove_rate'] = \
            float(self.nbgen.total_flows) / results_thread['end_to_end_flows_operation_time']

        # Remove switch time: Time from the first delete REST
        #                     request until all flows are removed from the
        #                     network.
        results['remove_switch_time'] = \
            results_thread['switch_operation_time']
        results['remove_switch_rate'] = \
            float(self.nbgen.total_flows) / results_thread['switch_operation_time']

        # Remove confirm time: Time period started after the last
        #                      flow was unconfigured until we receive
        #                      confirmation all flows are removed.
        results['remove_confirm_time'] = results_thread['confirm_time']
        results['remove_confirm_rate'] = \
            float(self.nbgen.total_flows) / results_thread['confirm_time']

        results['total_failed_flows_operations'] = total_failed_flows
        results['flow_delete_flag'] = 'False'
        #results.append(results)
        return results
