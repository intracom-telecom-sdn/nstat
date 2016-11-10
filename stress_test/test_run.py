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
import stress_test.oftraf
import sys
import time


class TestRun:

    def __init__(self, args, json_conf):
        """
        """
        self.controller = stress_test.controller.Controller.new(args.ctrl_base_dir,
                                                           json_conf)
        self.sb_emu = stress_test.emulator.SBEmu.new(args.sb_emu_base_dir,
                                                     json_conf)
        self.oftraf = stress_test.oftraf.Oftraf(self, self.controller,
                                                json_conf)
        self.test = stress_test.test_type.TestType(self,args)

    def sb_active_scalability_cbench_run(self, json_conf,
                                         ctrl_base_dir,
                                         sb_emu_base_dir,
                                         json_output,
                                         output_dir):
        """
        """
        try:

            # CONTROLLER preparation
            #-------------------------------------------------------------------
            self.controller.init_ssh()
            self.controller.build()

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

    def sb_active_stability_cbench_run(self):
        """
        """
        try:
            # CONTROLLER preparation
            #-------------------------------------------------------------------
            self.controller.init_ssh()
            self.controller.build()

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
            #-------------------------------------------------------------------
            self.controller.init_ssh()
            self.controller.build()

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

    def sb_active_scalability_multinet_run(self,
                                           json_conf,
                                           ctrl,
                                           ctrl_base_dir,
                                           sb_emu,
                                           sb_gen_base_dir,
                                           oftraf,
                                           oftraf_path,
                                           mon,
                                           json_output,
                                           output_dir):
        """
        """
        mon = self.mon = stress_test.monitor.Monitor(self)

        try:
            # CONTROLLER preparation
            # ---------------------------------------------------------------
            ctrl.init_ssh()
            ctrl.build()
            logging.info('[sb_active_scalability_multinet] Controller files '
                         'have been created')

            # EMULATOR preparation
            # ---------------------------------------------------------------
            sb_emu.init_ssh()
            sb_emu.build()

            logging.info('[sb_active_scalability_multinet] Build a {0} '
                         'emulator on {1} host'.format(sb_emu.name, sb_emu.ip))

            # Oftraf preparation
            # ---------------------------------------------------------------
            oftraf.build()

            # TEST run
            # ---------------------------------------------------------------

            for (sb_emu.topo_size,
                 sb_emu.topo_type,
                 sb_emu.topo_hosts_per_switch,
                 sb_emu.topo_group_size,
                 sb_emu.topo_group_delay_ms
                 ) in itertools.product(
                    json_conf['multinet_topo_size'],
                    json_conf['multinet_topo_type'],
                    json_conf['multinet_topo_hosts_per_switch'],
                    json_conf['multinet_topo_group_size'],
                    json_conf['multinet_topo_group_delay_ms']):

                    # start a controller
                oftraf.start()
                ctrl.check_status()
                ctrl.start()

                sb_emu.deploy(ctrl.ip, ctrl.of_port)
                logging.info('[sb_active_scalability_multinet] '
                             'Generate multinet config file')

                sb_emu.init_topos()
                sb_emu.start_topos()
                time.sleep(10)
                logging.info("The whole number of switches are: {0}"
                             .format(sb_emu.get_switches()))
                logging.info("The whole number of flows are: {0}"
                             .format(sb_emu.get_flows()))

                sb_emu.generate_traffic()

                mon.monitor_run()

                # Stop/clean nodes
                # ---------------------------------------------------------
                ctrl.stop()
                ctrl.check_status()
                sb_emu.init_topos()
                oftraf.stop()
                sb_emu.cleanup()

            logging.info('[Testing] All done!')

        except:
            logging.error('{0} ::::::: Exception ::::::::'.format(test_type))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error('{0} Exception: {1}, {2}'.
                          format(test_type, exc_type, exc_tb.tb_lineno))

            errors = str(exc_obj).rstrip().split('\n')
            for error in errors:
                logging.error('{0} {1}'.format(test_type, error))
            logging.exception('')

        finally:

            common.generate_json_results(mon.results, json_output)
            try:
                ctrl.stop()
            except:
                pass

# copy_dir_remote_to_local?
            if ctrl.need_cleanup:
                ctrl.clean_hnd()
            try:
                sb_emu.cleanup()
            except:
                pass
            try:
                oftraf.stop()
            except:
                pass

            sb_emu.clean()
            common.close_ssh_connections([ctrl._ssh_conn])


    def sb_idle_scalability_multinet_run(self):
        """
        """
        try:
            # CONTROLLER preparation
            #-------------------------------------------------------------------
            self.controller.init_ssh()
            self.controller.build()

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
            self.controller.init_ssh()
            self.controller.build()

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
            self.controller.init_ssh()
            self.controller.build()

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