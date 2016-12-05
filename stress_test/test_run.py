# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import itertools
import json
import logging
import shutil
import stress_test.common
import stress_test.controller
import stress_test.emulator
import stress_test.monitor
import stress_test.nb_generator
import stress_test.oftraf
import stress_test.report_gen
import stress_test.report_spec_templates
# import stress_test.test_type
import sys
import time


class TestRun:

    def __init__(self, args, json_conf, test_type):
        """
        """
        self.ctrl = stress_test.controller.Controller.new(args.ctrl_base_dir,
                                                          json_conf)
        self.sb_emu = stress_test.emulator.SBEmu.new(args.sb_emu_base_dir,
                                                     json_conf)
        if 'sb_emulator_name' in json_conf:
            if json_conf['sb_emulator_name'] == "MTCBENCH":
                self.mon = stress_test.monitor.Mtcbench(self.ctrl,
                                                        self.sb_emu)
            else:
                pass

        if 'nb_emulator_name' in json_conf:
            self.mon = stress_test.monitor.Mtcbench(self.ctrl,
                                                    self.sb_emu)

            self.nb_emu = stress_test.nb_generator.NBgen(args.nb_emu_base_dir,
                                                         json_conf,
                                                         self.ctrl,
                                                         self.sb_emu)
        self.total_samples = []
        self.report_spec_templates = \
            stress_test.report_spec_templates.TestReport(test_type,
                                                         args.json_config)
        self.test_type = test_type
        self.json_conf = json_conf
        self.args = args

    def sb_active_scalability_cbench_run(self,
                                         json_conf,
                                         json_output,
                                         output_dir):
        """
        Runs the SouthBound scalability test with active MT-Cbench switches
        :param json_conf: JSON configuration dictionary
        :param json_output: JSON output file (results)
        :param output_dir: directory to store output files
        :type json_conf: str
        :type json_output: str
        :type output_dir: str
        """
        # CONTROLLER preparation
        # ------------------------------------------------------------------
        self.ctrl.init_ssh()
        self.ctrl.build()

        # EMULATOR preparation
        # ----------------------------------------------------------------
        self.sb_emu.init_ssh()
        self.sb_emu.build()
        self.ctrl.generate_xmls()
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
                                    json_conf['mtcbench_thread_creation_'
                                              'delay_ms'],
                                    json_conf['mtcbench_delay_before_traffic'
                                              '_ms'],
                                    json_conf['mtcbench_simulated_hosts'],
                                    list(range(0, json_conf['test_repeats'])),
                                    json_conf['controller_statistics_period_'
                                              'ms']):
            self.mon.global_sample_id = global_sample_id
            self.mon.repeat_id = repeat_id
            self.mon.test_repeats = json_conf['test_repeats']
            logging.info('{0} Changing controller statistics period to {1} ms'.
                         format(self.test_type, self.ctrl.stat_period_ms))
            self.ctrl.change_stats()
            logging.info('{0} Starting controller'.format(self.test_type))
            self.ctrl.start()
            logging.info('{0} Starting MTCbench active switches topology and '
                         'monitor thread'.format(self.test_type))
            self.total_samples += self.mon.monitor_run()
            # total_samples = self.mon.monitor_run()
            logging.info('{0} Stopping controller'.format(self.test_type))
            self.ctrl.stop()
            global_sample_id += 1
        logging.info('[Testing] All done!')
        logging.info('[{0}] Generating results report.'.format(self.test_type))
        self.results_report(json_conf)

    def sb_active_stability_cbench_run(self,
                                       json_conf,
                                       json_output,
                                       output_dir):
        """
        Runs the SouthBound stability test with active MT-Cbench switches
        :param json_conf: JSON configuration dictionary
        :param json_output: JSON output file (results)
        :param output_dir: directory to store output files
        :type json_conf: str
        :type json_output: str
        :type output_dir: str
        """

        # CONTROLLER preparation
        # ------------------------------------------------------------------
        self.ctrl.init_ssh()
        self.ctrl.build()

        # EMULATOR preparation
        # ------------------------------------------------------------------
        self.sb_emu.init_ssh()
        self.sb_emu.build()

        # TEST run
        # ------------------------------------------------------------------
        # run tests for all possible dimensions
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
            self.ctrl.change_stats()
            self.ctrl.start()
            # total_samples = self.mon.monitor_run()
            self.ctrl.stop()
        logging.info('[{0}] Generating results report.'.format(self.test_type))
        self.results_report(json_conf)

    def sb_idle_scalability_cbench_run(self,
                                       json_conf,
                                       json_output,
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

        # CONTROLLER preparation
        # ------------------------------------------------------------------
        self.ctrl.init_ssh()
        self.ctrl.build()

        # EMULATOR preparation
        # ----------------------------------------------------------------
        self.sb_emu.init_ssh()
        self.sb_emu.build()
        self.ctrl.generate_xmls()
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
            logging.info('{0} Changing controller statistics period to {1} ms'.
                         format(self.test_type, self.ctrl.stat_period_ms))
            self.ctrl.change_stats()
            logging.info('{0} Starting controller'.format(self.test_type))
            self.ctrl.start()
            logging.info('{0} Starting MTCbench idle switches topology and '
                         'monitor thread'.format(self.test_type))
            topo_start_timestamp = time.time()
            self.total_samples += self.mon.monitor_run(topo_start_timestamp)
            # total_samples = self.mon.monitor_run()
            logging.info('{0} Stopping controller'.format(self.test_type))
            self.ctrl.stop()
            global_sample_id += 1
        logging.info('[Testing] All done!')
        logging.info('[{0}] Generating results report.'.format(self.test_type))
        self.results_report(json_conf)

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
            # CONTROLLER preparation
            # ---------------------------------------------------------------
            self.ctrl.init_ssh()

            # build a controller
            self.ctrl.build()
            host = self.ctrl.ssh_user + '@' + self.ctrl.ip
            logging.info('[sb_active_scalability_multinet] Build a controller '
                         'on {} host.'.format(host))

            self.ctrl.generate_xmls()

            # EMULATOR preparation
            # ---------------------------------------------------------------
            self.sb_emu.init_ssh()
            self.sb_emu.build()

            logging.info('[sb_active_scalability_multinet] Build a {0} '
                         'emulator on {1} host'.format(self.sb_emu.name,
                                                       self.sb_emu.ip))

            self.ctrl.generate_xmls()
            self.ctrl.flowmods_config()
            # TEST run
            # ---------------------------------------------------------------
            of = stress_test.oftraf.Oftraf(self.ctrl, json_conf)
            monitor = stress_test.monitor.Multinet(self.ctrl,
                                                   of,
                                                   self.sb_emu)
            of.build()
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
                monitor.global_sample_id = global_sample_id
                # start a controller
                self.ctrl.check_status()
                self.ctrl.start()

                # disable persistence
                if self.ctrl.persistence_hnd:
                    self.ctrl.disable_persistence()

                of.start()
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

                self.total_samples += monitor.monitor_run()

                # Stop/clean nodes
                # ---------------------------------------------------------
                of.stop()
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
                of.clean()
            except:
                pass
            try:
                logging.info('[{0}] Generating results report.'.
                             format(self.test_type))
                self.results_report(json_conf)
            except:
                logging.error('[{0}] Fail to generate report.')
            del self.ctrl
            del self.sb_emu

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

        # CONTROLLER preparation
        # ------------------------------------------------------------------
        self.ctrl.init_ssh()
        self.ctrl.build()

        # EMULATOR preparation
        # ------------------------------------------------------------------
        self.sb_emu.init_ssh()
        self.sb_emu.build()

        # TEST run
        # ------------------------------------------------------------------
        for (self.sb_emu.topo_size,
             self.sb_emu.topo_group_size,
             self.sb_emu.topo_group_delay_ms,
             self.sb_emu.topo_hosts_per_switch,
             self.sb_emu.topo_type,
             self.ctrl.stat_period_ms
             ) in itertools.product(json_conf['multinet_topo_size'],
                                    json_conf['multinet_topo_group_size'],
                                    json_conf['multinet_topo_group_delay_ms'],
                                    json_conf['multinet_topo_hosts_per_'
                                              'switch'],
                                    json_conf['multinet_topo_type'],
                                    json_conf['controller_statistics_'
                                              'period_ms']):
            self.ctrl.generate_xml()
            self.ctrl.change_stats()
            self.ctrl.start()

            self.sb_emu.deploy(json_conf['controller_node_ip'],
                               json_conf['controller_port'])

            self.sb_emu.init_topos()
            self.sb_emu.start_topos()
            self.ctrl.stop()
        logging.info('[{0}] Generating results report.'.format(self.test_type))
        self.results_report(json_conf)

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

        # CONTROLLER preparation
        # ------------------------------------------------------------------
        self.ctrl.init_ssh()
        self.ctrl.build()

        # EMULATOR preparation
        # ------------------------------------------------------------------
        self.sb_emu.init_ssh()
        self.sb_emu.build()

        # TEST run
        # ------------------------------------------------------------------
        # for sample_id in list(range(json_conf['number_of_samples'] + 1)):
        #    pass

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

        # CONTROLLER preparation
        # ------------------------------------------------------------------
        self.ctrl.init_ssh()
        self.ctrl.build()

        # SB EMULATOR preparation
        # ------------------------------------------------------------------
        self.sb_emu.init_ssh()
        self.sb_emu.build()

        # NB EMULATOR preparation
        # ------------------------------------------------------------------
        self.nb_emu.init_ssh()
        self.nb_emu.build()

        # TEST run
        # ------------------------------------------------------------------
        for (self.nb_emu.total_flows,
             self.nb_emu.flow_operations_delay_ms,
             self.sb_emu.topo_size,
             self.nb_emu.flow_workers,
             self.sb_emu.topo_group_size,
             self.sb_emu.topo_group_delay_ms,
             self.sb_emu.topo_hosts_per_switch,
             self.sb_emu.topo_type,
             self.ctrl.stat_period_ms) in \
                 itertools.product(json_conf['total_flows'],
                                   json_conf['flow_operations_delay_ms'],
                                   json_conf['multinet_topo_size'],
                                   json_conf['flow_workers'],
                                   json_conf['multinet_topo_group_size'],
                                   json_conf['multinet_topo_group_delay_ms'],
                                   json_conf['multinet_topo_hosts_per_switch'],
                                   json_conf['multinet_topo_type'],
                                   json_conf['controller_statistics_period_ms']):
            self.ctrl.check_status()
            self.ctrl.start()
            self.sb_emu.deploy(self.ctrl.ip, self.ctrl.of_port)
            self.sb_emu.init_topos()
            self.sb_emu.start_topos()
            self.nb_emu.run()
            self.sb_emu.generate_traffic()

            #monitor = stress_test.monitor.NBgen(self.ctrl,
            #                                    self.nb_emu,
            #                                    self.sb_emu)
            # ------------------------------------------------------------------
            # ------------------------------------------------------------------
            # ------------------------------------------------------------------
            print('===========================================================')
            print('===========================================================')
            print('===========================================================')
            print('===========================================================')
            initial_topology_flows = self.sb_emu.get_flows()
            initial_operational_ds_flows = self.nb_emu.get_oper_ds_flows()
            logging.info("initial_operational_ds_flows: {0}".
                         format(initial_operational_ds_flows))
            print('===========================================================')
            print('===========================================================')
            print('===========================================================')
            print('===========================================================')
            exit()
            '''
            if (initial_operational_ds_flows != 0 or initial_topology_flows != 0):
                raise ValueError('Initial installed flows were not equal to 0.')

            add_failed_flows_operations = 0
            delete_failed_flows_operations = 0
            result_metrics_add = {}
            result_metrics_del = {}
            start_rest_request_time = time.time()

            nb_generator_start_json_output = self.nb_emu.run()

            nb_generator_start_output = json.loads(nb_generator_start_json_output)



            add_failed_flows_operations = nb_generator_start_output[0]
            add_controller_time = time.time() - start_rest_request_time


            result_metrics_add.update(monitor.monitor_threads_run(start_rest_request_time))

            end_to_end_installation_time = result_metrics_add['end_to_end_flows_operation_time']
            add_switch_time = result_metrics_add['switch_operation_time']
            add_confirm_time = result_metrics_add['confirm_time']
            exit()
            # ------------------------------------------------------------------
            # ------------------------------------------------------------------
            # ------------------------------------------------------------------
            self.sb_emu.cleanup()
            self.ctrl.stop()
            self.ctrl.check_status()
            '''
        logging.info('[Testing] All done!')
        logging.info('[{0}] Generating results report.'.format(self.test_type))
        self.results_report(json_conf)

    def results_report(self, json_conf):
        report_spec = self.report_spec_templates.sb_active_scalability_multinet(
            self.args.json_output)
        report_gen = stress_test.report_gen.ReportGen(
            self.args, json_conf, self.total_samples, report_spec)
        try:
            report_gen.generate_json_results()
            report_gen.generate_plots()
            report_gen.generate_html_report()
            report_gen.save_controller_log()
            shutil.copy(self.args.json_config, self.args.output_dir)
        except:
            logging.error('[results_report] Failure during results generation.'
                          ' Check if older results are present and clean them '
                          'or if you have write permissions o the result '
                          'destination folder.')
        finally:
            del report_spec
            del report_gen
