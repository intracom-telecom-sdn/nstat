# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import os
import stress_test.controller
import stress_test.emulator
import time
import util.file_ops
import util.netutil
import util.process
import queue


class TestRun:

    def __init__(self, args, json_conf):
        """
        """
        self.controller = stress_test.controller.Controller.new(args.ctrl_base_dir,
                                                           json_conf)
        self.sb_emulator = stress_test.emulator.SBEmu.new(args.sb_emu_base_dir,
                                                     json_conf)
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
            self.sb_emulator.init_ssh()
            self.sb_emulator.build()


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
            self.sb_emulator.init_ssh()
            self.sb_emulator.build()

            exit()

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
            self.sb_emulator.init_ssh()
            self.sb_emulator.build()

            exit()

            # TEST run
            #-------------------------------------------------------------------

        except:
            pass

        finally:
            pass

    def sb_active_scalability_multinet_run(self):
        """
        """
        try:
            # CONTROLLER preparation
            #-------------------------------------------------------------------
            self.controller.init_ssh()
            self.controller.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            self.sb_emulator.init_ssh()
            self.sb_emulator.build()

            exit()
            # TEST run
            #-------------------------------------------------------------------

        except:
            pass

        finally:
            pass


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
            self.sb_emulator.init_ssh()
            self.sb_emulator.build()

            exit()

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
            self.sb_emulator.init_ssh()
            self.sb_emulator.build()

            exit()

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
            self.sb_emulator.init_ssh()
            self.sb_emulator.build()

            exit()

            # TEST run
            #-------------------------------------------------------------------

        except:
            pass

        finally:
            pass