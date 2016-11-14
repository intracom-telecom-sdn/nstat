# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import itertools
import logging
import common
import stress_test.controller
import stress_test.emulator
import stress_test.monitor
import stress_test.oftraf
# import stress_test.test_type
import sys
import time


class TestRun:

    def __init__(self, args, json_conf):
        """
        """
        self.ctrl = stress_test.controller.Controller.new(args.ctrl_base_dir,
                                                          json_conf)
        self.sb_emu = stress_test.emulator.SBEmu.new(args.sb_emu_base_dir,
                                                     json_conf)
        # self.test = stress_test.test_type.TestType(self, args)

        '''
        if self.sb_emu. == MTCBENCH
            self.mon = stress_test.monitor.Mtcbench(self, self.ctrl, self.sb_emu)
        elif: self.sb_emu. == MULTINET
            self.mon = stress_test.monitor.Multinet(self, self.ctrl, self.sb_emu)
        else
        '''

    def sb_active_scalability_cbench_run(self,
                                         json_conf,
                                         json_output,
                                         output_dir):
        """
        """
        # CONTROLLER preparation
        #-------------------------------------------------------------------
        self.ctrl.init_ssh()
        self.ctrl.build()

        # EMULATOR preparation
        #-------------------------------------------------------------------
        self.sb_emu.init_ssh()
        self.sb_emu.build()

        # TEST run
        #-------------------------------------------------------------------
        for (self.sb_emu.threads,
             self.sb_emu.switches_per_thread,
             self.sb_emu.thread_creation_delay_ms,
             self.sb_emu.delay_before_traffic_ms,
             self.sb_emu.simulated_hosts,
             self.repeat_id,
             self.ctrl.stat_period) in itertools.product(json_conf['mtcbench_threads'],
                               json_conf['mtcbench_switches_per_thread'],
                               json_conf['mtcbench_thread_creation_delay_ms'],
                               json_conf['mtcbench_delay_before_traffic_ms'],
                               json_conf['mtcbench_simulated_hosts'],
                               list(range(0, json_conf['test_repeats'])),
                               json_conf['controller_statistics_period_ms']):
            print("Kostas Papadopoulos (within loop)")
            # Change controller statistics period to controller statistics period in ms
            #self.ctrl.change_stats()
            #self.ctrl.start()
            #self.ctrl.stop()

    def sb_active_stability_cbench_run(self):
        """
        """
        try:
            # CONTROLLER preparation
            #-------------------------------------------------------------------
            self.ctrl.init_ssh()
            self.ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            self.sb_emu.init_ssh()
            self.sb_emu.build()

            # TEST run
            #-------------------------------------------------------------------

        except:
            pass
        finally:
            pass

    def sb_idle_scalability_cbench_run(self):
        """
        """
        try:
            # CONTROLLER preparation
            # ------------------------------------------------------------------
            self.ctrl.init_ssh()
            self.ctrl.build()

            # EMULATOR preparation
            # ----------------------------------------------------------------
            self.sb_emu.init_ssh()
            self.sb_emu.build()

            # TEST run
            # ----------------------------------------------------------------

        except:
            pass

        finally:
            pass

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
        self.ctrl.build()
        logging.info('[sb_active_scalability_multinet] Controller files '
                     'have been created')

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

        # TEST run
        # ---------------------------------------------------------------

        for (self.sb_emu.topo_size,
             self.sb_emu.topo_type,
             self.sb_emu.topo_hosts_per_switch,
             self.sb_emu.topo_group_size,
             self.sb_emu.topo_group_delay_ms
             ) in itertools.product(
                json_conf['multinet_topo_size'],
                json_conf['multinet_topo_type'],
                json_conf['multinet_topo_hosts_per_switch'],
                json_conf['multinet_topo_group_size'],
                json_conf['multinet_topo_group_delay_ms']):

            i = 1
            print("{0} repetition".format(i))
            # start a controller
            self.ctrl.check_status()
            self.ctrl.start()
            self.oftraf = stress_test.oftraf.Oftraf(self.ctrl, json_conf)
            self.oftraf.start()

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

            # mon.monitor_run()

            # Stop/clean nodes
            # ---------------------------------------------------------
            self.ctrl.stop()
            self.ctrl.check_status()
            self.sb_emu.init_topos()
            self.oftraf.stop()
            self.sb_emu.cleanup()
            i+=1

        logging.info('[Testing] All done!')

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

        # common.generate_json_results(mon.results, json_output)
        try:
            self.ctrl.stop()
        except:
            pass

# copy_dir_remote_to_local?
        if self.ctrl.need_cleanup:
            self.ctrl.clean_hnd()
        try:
            self.sb_emu.cleanup()
        except:
            pass
        try:
            self.oftraf.stop()
        except:
            pass

        self.sb_emu.clean()
        common.close_ssh_connections([self.ctrl._ssh_conn])


    def sb_idle_scalability_multinet_run(self):
        """
        """
        try:
            # CONTROLLER preparation
            #-------------------------------------------------------------------
            self.ctrl.init_ssh()
            self.ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            self.sb_emu.init_ssh()
            self.sb_emu.build()

            # TEST run
            #-------------------------------------------------------------------

        except:
            pass

        finally:
            pass
    def sb_idle_stability_multinet_run(self):
        """
        """
        try:
            # CONTROLLER preparation
            #-------------------------------------------------------------------
            self.ctrl.init_ssh()
            self.ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            self.sb_emu.init_ssh()
            self.sb_emu.build()

            # TEST run
            #-------------------------------------------------------------------

        except:
            pass

        finally:
            pass

    def nb_active_scalability_multinet_run(self):
        """
        """
        try:
            # CONTROLLER preparation
            #-------------------------------------------------------------------
            self.ctrl.init_ssh()
            self.ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            self.sb_emu.init_ssh()
            self.sb_emu.build()

            # TEST run
            #-------------------------------------------------------------------

        except:
            pass

        finally:
            pass