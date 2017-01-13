# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Test run class. Here we define the different type of test run methods for
each test"""

import itertools
import json
import logging
import stress_test.controller
import stress_test.emulator
import stress_test.monitor
import stress_test.nb_generator
import stress_test.oftraf
import sys
import time
import util.file_ops


class TestRun:

    def __init__(self, args, json_conf, test_type):
        """
        Initializes the appropriate test component objects according to the
        test_type and the test configuration json object, in order to prepare
        the test for running
        :param args:
        :param json_conf:
        :param test_type:
        :type args:
        :type json_conf:
        :type test_type: str
        """
        # CONTROLLER preparation
        # ----------------------------------------------------------------------
        self.ctrl = stress_test.controller.Controller.new(args.ctrl_base_dir,
                                                          json_conf)
        self.ctrl.init_ssh()
        self.ctrl.build()
        self.ctrl.generate_xmls()

        # SB EMULATOR preparation
        # ----------------------------------------------------------------------
        self.sb_emu = stress_test.emulator.SBEmu.new(args.sb_emu_base_dir,
                                                     json_conf)
        self.sb_emu.init_ssh()
        self.sb_emu.build()

        # NB EMULATOR preparation
        # ----------------------------------------------------------------------
        if 'nb_emulator_name' in json_conf:
                self.nb_emu = stress_test.nb_generator.NBgen(
                    args.nb_emu_base_dir,
                    json_conf,
                    self.ctrl,
                    self.sb_emu)
                self.nb_emu.init_ssh()
                self.nb_emu.build()

        # Monitor object for nb-emulator---------------------------------------
                self.mon = stress_test.monitor.NBgen(self.ctrl,
                                                     self.nb_emu,
                                                     self.sb_emu)

        # Monitor objects for sb-emulators
        elif 'sb_emulator_name' in json_conf:
            if json_conf['sb_emulator_name'] == "MTCBENCH":
                self.mon = stress_test.monitor.Mtcbench(self.ctrl,
                                                        self.sb_emu)
            elif json_conf['sb_emulator_name'] == "MULTINET":
                if 'oftraf_rest_server_port' in json_conf:
                    self.of = stress_test.oftraf.Oftraf(self.ctrl, json_conf)
                else:
                    self.of = None
                self.mon = stress_test.monitor.Multinet(self.ctrl,
                                                        self.of,
                                                        self.sb_emu)
        else:
            pass

        self.total_samples = []
        self.test_type = test_type
        self.json_conf = json_conf
        self.args = args

    def sb_active_stability_mtcbench_run(self, json_conf, json_output,
                                         output_dir):
        """
        Runs the SouthBound scalability or stability test with active
        MT-Cbench switches
        :param json_conf: JSON configuration dictionary
        :param json_output: JSON output file (results)
        :param output_dir: directory to store output files
        :type json_conf: str
        :type json_output: str
        :type output_dir: str
        """
        try:

            global_sample_id = 0
            # TEST run
            # -------------------------------------------------------------------
            for (self.sb_emu.threads,
                 self.sb_emu.switches_per_thread,
                 self.sb_emu.thread_creation_delay_ms,
                 self.sb_emu.delay_before_traffic_ms,
                 self.sb_emu.simulated_hosts,
                 repeat_id,
                 self.ctrl.stat_period_ms
                 ) in itertools.product(json_conf['mtcbench_threads'],
                                        json_conf['mtcbench_switches_per_thread'],
                                        json_conf['mtcbench_thread_creation_delay_ms'],
                                        json_conf['mtcbench_delay_before_traffic_ms'],
                                        json_conf['mtcbench_simulated_hosts'],
                                        list(range(0, json_conf['test_repeats'])),
                                        json_conf['controller_statistics_period_ms']):
                self.mon.global_sample_id = global_sample_id
                self.mon.repeat_id = repeat_id
                self.mon.test_repeats = json_conf['test_repeats']
                logging.info('[{0}] Changing controller statistics period to'
                             ' {1} ms'.format(self.test_type,
                                              self.ctrl.stat_period_ms))
                self.ctrl.change_stats()
                logging.info('[{0}] Starting controller'.
                             format(self.test_type))
                self.ctrl.start()
                logging.info('[{0}] Starting MTCbench active switches '
                             'topology and monitor thread'.
                             format(self.test_type))
                self.total_samples += self.mon.monitor_run()
                logging.info('[{0}] Stopping controller'.
                             format(self.test_type))
                self.ctrl.stop()
                global_sample_id = \
                    self.total_samples[-1]['global_sample_id'] + 1
            logging.info('[Testing] All done!')
        except:
            logging.error('[{0}] Exiting test run'.format(self.test_type))
        finally:
            try:
                logging.info('[{0}] Save controller logs'.
                             format(self.test_type))
                self.ctrl.save_log(output_dir)
            except:
                logging.error('[{0}] Fail to save controller logs'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean controller.'.
                             format(self.test_type))
                del self.ctrl
            except:
                logging.error('[{0}] Fail to cleanup controller.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean mtcbench.'.
                             format(self.test_type))
                del self.sb_emu
            except:
                logging.error('[{0}] Fail to clean mtcbench.'.
                              format(self.test_type))

            return self.total_samples

    def sb_active_scalability_mtcbench_run(self, json_conf, json_output,
                                           output_dir):
        """
        Runs the SouthBound scalability or stability test with active
        MT-Cbench switches
        :param json_conf: JSON configuration dictionary
        :param json_output: JSON output file (results)
        :param output_dir: directory to store output files
        :type json_conf: str
        :type json_output: str
        :type output_dir: str
        """
        try:

            global_sample_id = 0
            # TEST run
            # -------------------------------------------------------------------
            for (self.sb_emu.threads,
                 self.sb_emu.switches_per_thread,
                 self.sb_emu.thread_creation_delay_ms,
                 self.sb_emu.delay_before_traffic_ms,
                 self.sb_emu.simulated_hosts,
                 repeat_id,
                 self.ctrl.stat_period_ms
                 ) in itertools.product(json_conf['mtcbench_threads'],
                                        json_conf['mtcbench_switches_per_thread'],
                                        json_conf['mtcbench_thread_creation_delay_ms'],
                                        json_conf['mtcbench_delay_before_traffic_ms'],
                                        json_conf['mtcbench_simulated_hosts'],
                                        list(range(0, json_conf['test_repeats'])),
                                        json_conf['controller_statistics_period_ms']):
                self.mon.global_sample_id = global_sample_id
                self.mon.repeat_id = repeat_id
                self.mon.test_repeats = json_conf['test_repeats']
                logging.info('[{0}] Changing controller statistics period to'
                             ' {1} ms'.format(self.test_type,
                                              self.ctrl.stat_period_ms))
                self.ctrl.change_stats()
                logging.info('[{0}] Starting controller'.
                             format(self.test_type))
                self.ctrl.start()
                logging.info('[{0}] Starting MTCbench active switches '
                             'topology and monitor thread'.
                             format(self.test_type))
                self.total_samples += self.mon.monitor_run()
                logging.info('[{0}] Stopping controller'.
                             format(self.test_type))
                self.ctrl.stop()
                global_sample_id = \
                    self.total_samples[-1]['global_sample_id'] + 1
            logging.info('[Testing] All done!')
        except:
            logging.error('[{0}] Exiting test run'.format(self.test_type))
        finally:
            try:
                logging.info('[{0}] Save controller logs'.
                             format(self.test_type))
                self.ctrl.save_log(output_dir)
            except:
                logging.error('[{0}] Fail to save controller logs'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean controller.'.
                             format(self.test_type))
                del self.ctrl
            except:
                logging.error('[{0}] Fail to cleanup controller.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean mtcbench.'.
                             format(self.test_type))
                del self.sb_emu
            except:
                logging.error('[{0}] Fail to clean mtcbench.'.
                              format(self.test_type))
            return self.total_samples

    def sb_idle_scalability_mtcbench_run(self, json_conf, json_output,
                                         output_dir):
        """
        Runs the SouthBound scalability test with idle MT-Cbench switches
        :param json_conf: JSON configuration dictionary
        :param json_output: JSON output file (results)
        :param output_dir: directory to store output files
        :type json_conf: str
        :type json_output: str
        :type output_dir: str
        """
        try:
            global_sample_id = 0
            # TEST run
            # ----------------------------------------------------------------
            for (self.sb_emu.threads,
                 self.sb_emu.switches_per_thread,
                 self.sb_emu.thread_creation_delay_ms,
                 self.sb_emu.delay_before_traffic_ms,
                 self.sb_emu.simulated_hosts,
                 self.ctrl.stat_period_ms
                 ) in itertools.product(json_conf['mtcbench_threads'],
                                        json_conf['mtcbench_switches_per_thread'],
                                        json_conf['mtcbench_thread_creation_delay_ms'],
                                        json_conf['mtcbench_delay_before_traffic_ms'],
                                        json_conf['mtcbench_simulated_hosts'],
                                        json_conf['controller_statistics_period_ms']):
                self.mon.global_sample_id = global_sample_id
                logging.info('{0} Changing controller statistics period '
                             'to {1} ms'.
                             format(self.test_type, self.ctrl.stat_period_ms))
                self.ctrl.change_stats()
                logging.info('{0} Starting controller'.format(self.test_type))
                self.ctrl.start()
                logging.info('{0} Starting MTCbench idle switches topology and'
                             ' monitor thread'.format(self.test_type))
                topo_start_timestamp = time.time()
                self.total_samples += self.mon.monitor_run(
                    topo_start_timestamp)
                # total_samples = self.mon.monitor_run()
                logging.info('{0} Stopping controller'.format(self.test_type))
                self.ctrl.stop()
                global_sample_id = self.total_samples[-1]['global_sample_id'] + 1
            logging.info('[Testing] All done!')
        except:
            logging.error('[{0}] Exiting test run'.format(self.test_type))
        finally:
            try:
                logging.info('[{0}] Save controller logs'.
                             format(self.test_type))
                self.ctrl.save_log(output_dir)
            except:
                logging.error('[{0}] Fail to save controller logs'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean controller.'.
                             format(self.test_type))
                del self.ctrl
            except:
                logging.error('[{0}] Fail to cleanup controller.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean mtcbench.'.
                             format(self.test_type))
                del self.sb_emu
            except:
                logging.error('[{0}] Fail to clean mtcbench.'.
                              format(self.test_type))
            return self.total_samples

    def sb_active_scalability_multinet_run(self,
                                           json_conf,
                                           json_output,
                                           output_dir):
        """
        Runs the SouthBound scalability test with active Multinet switches
        :param json_conf: JSON configuration dictionary
        :param json_output: JSON output file (results)
        :param output_dir: directory to store output files
        :type json_conf: str
        :type json_output: str
        :type output_dir: str
        """
        try:

            # Configuring controller for FLOWS_MODS
            # ------------------------------------------------------------------
            self.ctrl.flowmods_config()

            # OFTRAF preparation
            # ------------------------------------------------------------------
            self.of.build()

            # TEST run
            # ---------------------------------------------------------------
            global_sample_id = 0
            for (self.sb_emu.topo_size,
                 self.sb_emu.topo_type,
                 self.sb_emu.topo_hosts_per_switch,
                 self.sb_emu.topo_group_size,
                 self.sb_emu.topo_group_delay_ms,
                 self.ctrl.stat_period_ms
                 ) in itertools.product(
                    json_conf['multinet_topo_size'],
                    json_conf['multinet_topo_type'],
                    json_conf['multinet_topo_hosts_per_switch'],
                    json_conf['multinet_topo_group_size'],
                    json_conf['multinet_topo_group_delay_ms'],
                    json_conf['controller_statistics_period_ms']):
                self.mon.global_sample_id = global_sample_id
                self.mon.test_repeats = json_conf['test_repeats']
                # start a controller
                self.ctrl.check_status()
                self.ctrl.start()

                # disable persistence
                if self.ctrl.persistence_hnd:
                    self.ctrl.disable_persistence()

                self.of.start()
                self.sb_emu.deploy(self.ctrl.ip, self.ctrl.of_port)
                logging.info('[sb_active_scalability_multinet] '
                             'Generate multinet config file')
                self.sb_emu.init_topos()
                self.sb_emu.start_topos()
                time.sleep(10)
                logging.info("The whole number of switches are: {0}"
                             .format(self.sb_emu.get_switches()))
                logging.info("The whole number of flows are: {0}"
                             .format(self.sb_emu.get_flows()))

                self.sb_emu.generate_traffic()

                self.total_samples += self.mon.monitor_run()

                # Stop/clean nodes
                # ---------------------------------------------------------
                self.of.stop()
                self.ctrl.stop()

                self.sb_emu.stop_topos()
                self.sb_emu.cleanup()
                global_sample_id += 1

            logging.info('[Testing] All done!')
        except:
            logging.error('{0} ::::::: Exception ::::::::'.
                          format(self.test_type))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error('{0} Exception: {1}, {2}'.
                          format(self.test_type, exc_type, exc_tb.tb_lineno))
            errors = str(exc_obj).rstrip().split('\n')
            for error in errors:
                logging.error('{0} {1}'.format(self.test_type, error))
            logging.exception('')
        finally:
            try:
                logging.info('[{0}] Clean Multinet Monitor'.
                             format(self.test_type))
                del self.mon
            except:
                logging.error('[{0}] Fail to clean Multinet Monitor.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean Oftraf.'.
                             format(self.test_type))
                del self.of
            except:
                logging.error('[{0}] Fail to clean oftraf.'.
                              format(self.test_type))
            #try:
            logging.info('[{0}] Save controller logs'.
                         format(self.test_type))
            self.ctrl.save_log(output_dir)
            #except:
            #    logging.error('[{0}] Fail to save controller logs'.
            #                  format(self.test_type))
            try:
                logging.info('[{0}] Clean controller.'.
                             format(self.test_type))
                del self.ctrl
            except:
                logging.error('[{0}] Fail to cleanup controller.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean multinet.'.
                             format(self.test_type))
                del self.sb_emu
            except:
                logging.error('[{0}] Fail to clean multinet.'.
                              format(self.test_type))
            return self.total_samples

    def sb_idle_scalability_multinet_run(self,
                                         json_conf,
                                         json_output,
                                         output_dir):
        """
        Runs the SouthBound scalability test with idle Multinet switches
        :param json_conf: JSON configuration dictionary
        :param json_output: JSON output file (results)
        :param output_dir: directory to store output files
        :type json_conf: str
        :type json_output: str
        :type output_dir: str
        """
        try:
            global_sample_id = 0
            for (self.sb_emu.topo_size,
                 self.sb_emu.topo_group_size,
                 self.sb_emu.topo_group_delay_ms,
                 self.sb_emu.topo_hosts_per_switch,
                 self.sb_emu.topo_type,
                 self.ctrl.stat_period_ms
                 ) in itertools.product(json_conf['multinet_topo_size'],
                                        json_conf['multinet_topo_group_size'],
                                        json_conf['multinet_topo_group_'
                                                  'delay_ms'],
                                        json_conf['multinet_topo_hosts_per_'
                                                  'switch'],
                                        json_conf['multinet_topo_type'],
                                        json_conf['controller_statistics_'
                                                  'period_ms']):
                # start a controller
                self.mon.global_sample_id = global_sample_id
                self.ctrl.check_status()
                self.ctrl.change_stats()
                self.ctrl.start()
                # disable persistence
                if self.ctrl.persistence_hnd:
                    self.ctrl.disable_persistence()

                # start a Multinet topology
                self.sb_emu.deploy(self.ctrl.ip, self.ctrl.of_port)
                logging.info("{0} Starting Multinet idle switches topology".
                             format(self.test_type))
                self.sb_emu.init_topos()
                topo_start_timestamp = time.time()

                self.sb_emu.start_topos()
                self.total_samples += \
                    self.mon.monitor_run(boot_start_time=topo_start_timestamp)

                self.ctrl.stop()
                self.sb_emu.stop_topos()
                self.sb_emu.cleanup()

                global_sample_id =\
                    self.total_samples[-1]['global_sample_id'] + 1

            logging.info('[Testing] All done!')
        except:
            logging.error('{0} ::::::: Exception ::::::::'.
                          format(self.test_type))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error('{0} Exception: {1}, {2}'.
                          format(self.test_type, exc_type, exc_tb.tb_lineno))
            errors = str(exc_obj).rstrip().split('\n')
            for error in errors:
                logging.error('{0} {1}'.format(self.test_type, error))
            logging.exception('')

        finally:
            try:
                logging.info('[{0}] Clean Multinet Monitor'.
                             format(self.test_type))
                del self.mon
            except:
                logging.error('[{0}] Fail to clean Multinet Monitor.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Save controller logs'.
                             format(self.test_type))
                self.ctrl.save_log(output_dir)
            except:
                logging.error('[{0}] Fail to save controller logs'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean controller.'.
                             format(self.test_type))
                del self.ctrl
            except:
                logging.error('[{0}] Fail to cleanup controller.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean multinet.'.
                             format(self.test_type))
                del self.sb_emu
            except:
                logging.error('[{0}] Fail to clean multinet.'.
                              format(self.test_type))
        return self.total_samples

    def sb_idle_stability_multinet_run(self,
                                       json_conf,
                                       json_output,
                                       output_dir):
        """
        Runs the SouthBound stability test with idle Multinet switches
        :param json_conf: JSON configuration dictionary
        :param json_output: JSON output file (results)
        :param output_dir: directory to store output files
        :type json_conf: str
        :type json_output: str
        :type output_dir: str
        """
        try:
            # OFTRAF preparation
            # ------------------------------------------------------------------
            self.of.build()

            # TEST run
            # ---------------------------------------------------------------
            total_samples = []
            global_sample_id = 0

            self.sb_emu.topo_size = json_conf['multinet_topo_size']
            self.sb_emu.topo_type = json_conf['multinet_topo_type']
            self.sb_emu.topo_hosts_per_switch = json_conf['multinet_topo_'
                                                          'hosts_per_switch']
            self.sb_emu.topo_group_size = json_conf['multinet_topo_group_size']
            self.sb_emu.topo_group_delay_ms = json_conf['multinet_topo_group_'
                                                        'delay_ms']
            self.ctrl.stat_period_ms = json_conf['controller_statistics_'
                                                 'period_ms']

            # disable persistence if needed
            if self.ctrl.persistence_hnd:
                self.ctrl.disable_persistence()
            # start a controller
            self.ctrl.check_status()
            self.ctrl.change_stats()
            self.ctrl.start()

            # start a Multinet topology
            self.sb_emu.deploy(self.ctrl.ip, self.ctrl.of_port)
            self.sb_emu.init_topos()
            self.sb_emu.start_topos()

            self.of.start()

            logging.info("The whole number of switches are: {0}"
                         .format(self.sb_emu.get_switches()))
            logging.info("The whole number of flows are: {0}"
                         .format(self.sb_emu.get_flows()))

            reference_results = {'of_out_traffic': (0, 0),
                                 'of_in_traffic': (0, 0),
                                 'tcp_of_out_traffic': (0, 0),
                                 'tcp_of_in_traffic': (0, 0)}

            for sample_id in list(range(json_conf['number_of_samples'] + 1)):
                if sample_id > 0:
                    self.mon.global_sample_id = global_sample_id
                    results, reference_results = \
                        self.mon.monitor_run(
                            reference_results=reference_results,
                            sample_id=sample_id)
                    global_sample_id = results['global_sample_id'] + 1
                    self.total_samples += [results]

            # Stop/clean nodes
            # ---------------------------------------------------------
            self.of.stop()
            self.ctrl.stop()

            self.sb_emu.stop_topos()
            self.sb_emu.cleanup()
            global_sample_id += 1

            logging.info('[Testing] All done!')
        except:
            logging.error('{0} ::::::: Exception ::::::::'.
                          format(self.test_type))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error('{0} Exception: {1}, {2}'.
                          format(self.test_type, exc_type, exc_tb.tb_lineno))
            errors = str(exc_obj).rstrip().split('\n')
            for error in errors:
                logging.error('{0} {1}'.format(self.test_type, error))
            logging.exception('')

        finally:
            try:
                logging.info('[{0}] Clean Multinet Monitor'.
                             format(self.test_type))
                del self.mon
            except:
                logging.error('[{0}] Fail to clean Multinet Monitor.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean Oftraf.'.
                             format(self.test_type))
                del self.of
            except:
                logging.error('[{0}] Fail to clean oftraf.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Save controller logs'.
                             format(self.test_type))
                self.ctrl.save_log(output_dir)
            except:
                logging.error('[{0}] Fail to save controller logs'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean controller.'.
                             format(self.test_type))
                del self.ctrl
            except:
                logging.error('[{0}] Fail to cleanup controller.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean multinet.'.
                             format(self.test_type))
                del self.sb_emu
            except:
                logging.error('[{0}] Fail to clean multinet.'.
                              format(self.test_type))
            return self.total_samples

    def nb_active_scalability_multinet_run(self,
                                           json_conf,
                                           json_output,
                                           output_dir):
        """
        Runs the NorthBound scalability test with idle Multinet switches
        :param json_conf: JSON configuration dictionary
        :param json_output: JSON output file (results)
        :param output_dir: directory to store output files
        :type json_conf: str
        :type json_output: str
        :type output_dir: str
        """
        try:

            self.ctrl.flowmods_config()

            # TEST run
            # ---------------------------------------------------------------

            global_sample_id = 0
            flow_delete_flag = json_conf['flow_delete_flag']

            for (self.nb_emu.total_flows,
                 self.nb_emu.flow_operations_delay_ms,
                 self.sb_emu.topo_size,
                 self.nb_emu.flow_workers,
                 self.sb_emu.topo_group_size,
                 self.sb_emu.topo_group_delay_ms,
                 self.sb_emu.topo_hosts_per_switch,
                 self.sb_emu.topo_type,
                 self.ctrl.stat_period_ms
                 ) in itertools.product(
                     json_conf['total_flows'],
                     json_conf['flow_operations_delay_ms'],
                     json_conf['multinet_topo_size'],
                     json_conf['flow_workers'],
                     json_conf['multinet_topo_group_size'],
                     json_conf['multinet_topo_group_delay_ms'],
                     json_conf['multinet_topo_hosts_per_switch'],
                     json_conf['multinet_topo_type'],
                     json_conf['controller_statistics_period_ms']):

                self.mon.global_sample_id = global_sample_id

                # start a controller
                self.ctrl.check_status()
                self.ctrl.start()
                # disable persistence
                if self.ctrl.persistence_hnd:
                    self.ctrl.disable_persistence()
                self.sb_emu.deploy(self.ctrl.ip, self.ctrl.of_port)
                logging.info('[sb_active_scalability_multinet] '
                             'Generate multinet config file')
                self.sb_emu.init_topos()
                self.sb_emu.start_topos()
                time.sleep(10)
                logging.info("The whole number of switches are: {0}"
                             .format(self.sb_emu.get_switches()))
                logging.info("The whole number of flows are: {0}"
                             .format(self.sb_emu.get_flows()))

                initial_topo_flows = self.sb_emu.get_flows()
                initial_oper_ds_flows = self.ctrl.get_oper_flows()
                logging.info("initial_operational_ds_flows: {0}".
                             format(initial_oper_ds_flows))
                if (initial_oper_ds_flows != 0 or initial_topo_flows != 0):
                    raise ValueError('Initial installed flows '
                                     'were not equal to 0.')

                failed_flows_add = 0
                failed_flows_del = 0
                result_metrics_add = {}
                result_metrics_del = {}

                if flow_delete_flag is False:
                    expected_flows = self.nb_emu.total_flows
                    start_rest_request_time_add = time.time()
                    nb_gen_start_json_output_add = self.nb_emu.run()
                    nb_gen_start_output_add = json.loads(nb_gen_start_json_output_add)
                    failed_flows_add = nb_gen_start_output_add[0]

                    result_metrics_add = \
                        self.mon.monitor_threads_run(start_rest_request_time_add,
                                                     failed_flows_add,
                                                     expected_flows,
                                                     self.nb_emu.flow_delete_flag)

                # start northbound generator flow_delete_flag SET
                if flow_delete_flag is True:
                    # Force flow_delete_flag to FALSE and run the NB generator
                    self.nb_emu.flow_delete_flag = False
                    expected_flows = self.nb_emu.total_flows
                    start_rest_request_time_add = time.time()
                    nb_gen_start_json_output_add = self.nb_emu.run()
                    nb_gen_start_output_add = json.loads(nb_gen_start_json_output_add)
                    failed_flows_add = nb_gen_start_output_add[0]
                    result_metrics_add = \
                        self.mon.monitor_threads_run(start_rest_request_time_add,
                                                     failed_flows_add,
                                                     expected_flows,
                                                     self.nb_emu.flow_delete_flag)

                    # Restore constructor value for flow_delete_flag and run the
                    # NB generator
                    self.nb_emu.flow_delete_flag = True
                    expected_flows = 0
                    start_rest_request_time_del = time.time()
                    nb_gen_start_json_output_del = self.nb_emu.run()
                    nb_gen_start_output_del = json.loads(nb_gen_start_json_output_del)
                    failed_flows_del = nb_gen_start_output_del[0]

                    result_metrics_del = \
                        self.mon.monitor_threads_run(start_rest_request_time_del,
                                                     failed_flows_del,
                                                     expected_flows,
                                                     self.nb_emu.flow_delete_flag)
                failed_flows_total = failed_flows_add + failed_flows_del

                # Stop/clean nodes
                # ---------------------------------------------------------
                self.ctrl.stop()
                self.sb_emu.stop_topos()
                self.sb_emu.cleanup()
                results = util.file_ops.merge_dict_and_avg(result_metrics_add,
                                                           result_metrics_del)
                global_sample_id = results['global_sample_id'] + 1
                self.total_samples += [results]

        except:
            logging.error('{0} ::::::: Exception ::::::::'.
                          format(self.test_type))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error('{0} Exception: {1}, {2}'.
                          format(self.test_type, exc_type, exc_tb.tb_lineno))
            errors = str(exc_obj).rstrip().split('\n')
            for error in errors:
                logging.error('{0} {1}'.format(self.test_type, error))
            logging.exception('')

        finally:
            try:
                logging.info('[{0}] Clean NB-Generator.'.
                             format(self.test_type))
                del self.nb_emu
            except:
                logging.error('[{0}] Fail to clean NB-Generator.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean NB-Generator Monitor'.
                             format(self.test_type))
                del self.mon
            except:
                logging.error('[{0}] Fail to clean NB-Generator Monitor.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Save controller logs'.
                             format(self.test_type))
                self.ctrl.save_log(output_dir)
            except:
                logging.error('[{0}] Fail to save controller logs'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean controller.'.
                             format(self.test_type))
                del self.ctrl
            except:
                logging.error('[{0}] Fail to cleanup controller.'.
                              format(self.test_type))
            try:
                logging.info('[{0}] Clean multinet.'.
                             format(self.test_type))
                del self.sb_emu
            except:
                logging.error('[{0}] Fail to clean multinet.'.
                              format(self.test_type))
            return self.total_samples
