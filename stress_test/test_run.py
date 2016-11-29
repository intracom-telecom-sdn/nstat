# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import itertools
import logging
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
        self.report_spec_templates = stress_test.report_spec_templates.TestReport(
            test_type, args.json_config)
        self.test_type = test_type
        self.json_conf = json_conf
        self.args = args

    def sb_active_scalability_cbench_run(self,
                                         json_conf,
                                         json_output,
                                         output_dir):
        """
        """
        # CONTROLLER preparation
        # -------------------------------------------------------------------
        self.ctrl.init_ssh()
        self.ctrl.build()

        # EMULATOR preparation
        # -------------------------------------------------------------------
        self.sb_emu.init_ssh()
        self.sb_emu.build()

        # TEST run
        # -------------------------------------------------------------------
        for (self.sb_emu.threads,
             self.sb_emu.switches_per_thread,
             self.sb_emu.thread_creation_delay_ms,
             self.sb_emu.delay_before_traffic_ms,
             self.sb_emu.simulated_hosts,
             self.repeat_id,
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
            self.ctrl.change_stats()
            self.ctrl.start()
            self.total_samples = self.mon.monitor_run()
            self.ctrl.stop()

    def sb_active_stability_cbench_run(self,
                                       json_conf,
                                       json_output,
                                       output_dir):
        """
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
             self.repeat_id,
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

    def sb_idle_scalability_cbench_run(self,
                                       json_conf,
                                       json_output,
                                       output_dir):
        """
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

        # TEST run
        # ----------------------------------------------------------------
        for (self.sb_emu.threads,
             self.sb_emu.switches_per_thread,
             self.sb_emu.thread_creation_delay_ms,
             self.sb_emu.delay_before_traffic_ms,
             self.sb_emu.simulated_host,
             self.ctrl.stat_period_ms
             ) in itertools.product(json_conf['mtcbench_threads'],
                                    json_conf['mtcbench_switches_per_thread'],
                                    json_conf['mtcbench_thread_creation_'
                                              'delay_ms'],
                                    json_conf['mtcbench_delay_before_'
                                              'traffic_ms'],
                                    json_conf['mtcbench_simulated_hosts'],
                                    json_conf['controller_statistics_'
                                              'period_ms']):
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
        logging.info('[Testing] All done!')
        report_spec = self.report_spec_templates.sb_active_scalability_multinet(
            self.args.json_output)
        report_gen = stress_test.report_gen.ReportGen(
            self.args, json_conf, self.total_samples, report_spec)
        report_gen.generate_json_results()
        report_gen.generate_plots()
        report_gen.generate_html_report()
        report_gen.save_controller_log()

    def sb_active_scalability_multinet_run(self,
                                           json_conf,
                                           json_output,
                                           output_dir):
        """
        """
#        try:
        # CONTROLLER preparation
        # ---------------------------------------------------------------
        print("STARTING THE TEST")
        self.ctrl.init_ssh()

        # build a controller
        self.ctrl.build()
            # check the effect of build()
        host = self.ctrl.ssh_user + '@' + self.ctrl.ip
        logging.info('[sb_active_scalability_multinet] Build a controller '
                     'on {} host.'.format(host))

        if self.ctrl.persistence_hnd:
            # disable persistence
            self.ctrl.disable_persistence()

        self.ctrl.generate_xmls()

        # EMULATOR preparation
        # ---------------------------------------------------------------
        self.sb_emu.init_ssh()
        self.sb_emu.build()

        logging.info('[sb_active_scalability_multinet] Build a {0} '
                     'emulator on {1} host'.format(self.sb_emu.name,
                                                   self.sb_emu.ip))

        # Oftraf preparation
        # ---------------------------------------------------------------
        # self.oftraf.build()
        print("READY for the loop")
        i = 1
        self.ctrl.generate_xmls()
        self.ctrl.flowmods_config()
        # TEST run
        # ---------------------------------------------------------------

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

            print("repetition number: {0}".format(i))
            # start a controller
            self.ctrl.check_status()
            self.ctrl.start()

            if json_conf['sb_emulator_name'] == "MULTINET":
                print("CTRL obj CREATED")
                print(self.ctrl.ip)
                print("Create oftraf object")
                of = stress_test.oftraf.Oftraf(self.ctrl, json_conf)
                of.build()
                of.start()
                print("Oftraf STARTED object")
                print("Create Multinet object")
                monitor = stress_test.monitor.Multinet(self.ctrl,
                                                       of,
                                                       self.sb_emu)
                print(monitor)
#                exit()
# ---------------------------------------------DEBUG--------------------------

                # oftraf_node = stress_test.oftraf.Oftraf(self.ctrl, json_conf)
                # mon = stress_test.monitor.Multinet(self.ctrl,
                #                                   oftraf_node,
                #                                   self.sb_emu)
            else:
                raise NotImplementedError('Not supported yet')

            # self.oftraf = stress_test.oftraf.Oftraf(self.ctrl, json_conf)
            # self.oftraf.start()

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

            i = i + 1
            print('ITERATION IS DONE!!!!!!!!!!!!!')
            print('ITERATION IS DONE!!!!!!!!!!!!!')
            print('ITERATION IS DONE!!!!!!!!!!!!!')
            print('ITERATION IS DONE!!!!!!!!!!!!!')
            print('ITERATION IS DONE!!!!!!!!!!!!!')
            print('ITERATION IS DONE!!!!!!!!!!!!!')
            print(i)

        logging.info('[Testing] All done!')
        report_spec = self.report_spec_templates.sb_active_scalability_multinet(
            self.args.json_output)
        report_gen = stress_test.report_gen.ReportGen(
            self.args, self.json_conf, self.total_samples, report_spec)
        report_gen.generate_json_results()
        report_gen.generate_plots()
        report_gen.generate_html_report()
        report_gen.save_controller_log()
#        except:
        '''logging.error('{0} ::::::: Exception ::::::::'.format(test_type))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error('{0} Exception: {1}, {2}'.
                      format(test_type, exc_type, exc_tb.tb_lineno))

        errors = str(exc_obj).rstrip().split('\n')
        for error in errors:
            logging.error('{0} {1}'.format(test_type, error))
        logging.exception('')
        '''

#        finally:
        del self.ctrl
        del self.sb_emu

    def sb_idle_scalability_multinet_run(self,
                                         json_conf,
                                         json_output,
                                         output_dir):
        """
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

    def sb_idle_stability_multinet_run(self,
                                       json_conf,
                                       json_output,
                                       output_dir):
        """
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

            start_rest_request_time = time.time()

            self.nb_emu.run()
            self.nb_emu.monitor_threads_run(start_rest_request_time)
            self.sb_emu.cleanup()
            self.ctrl.stop()
            self.ctrl.check_status()

        logging.info('[Testing] All done!')
        report_spec = \
            self.report_spec_templates.sb_active_scalability_multinet(json_output)
        report_gen = stress_test.report_gen.ReportGen(self.args,
                                                      json_conf,
                                                      self.total_samples,
                                                      report_spec)
        report_gen.generate_json_results()
        report_gen.generate_plots()
        report_gen.generate_html_report()
        report_gen.save_controller_log()
