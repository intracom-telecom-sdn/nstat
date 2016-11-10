# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import os
import time
import util.file_ops
import util.netutil
import util.process
import queue


class TestRun:

    def __init__(self, args):
        """
        """

    def sb_active_scalability_cbench_run(self):
        """
        """
        try:
            print('Kostas Papadopoulos')
            exit()
            # CONTROLLER preparation
            #-------------------------------------------------------------------
            ctrl.init_ssh()
            ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            sbemu.init_ssh()
            sb_emu.build()

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
            ctrl.init_ssh()
            ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            sbemu.init_ssh()
            sb_emu.build()

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
            ctrl.init_ssh()
            ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            sb_emu.init_ssh()
            sb_emu.build()

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
            ctrl.init_ssh()
            ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            sb_emu.init_ssh()
            sb_emu.build()

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
            ctrl.init_ssh()
            ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            sb_emu.init_ssh()
            sb_emu.build()

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
            ctrl.init_ssh()
            ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            sb_emu.init_ssh()
            sb_emu.build()

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
            ctrl.init_ssh()
            ctrl.build()

            # EMULATOR preparation
            #-------------------------------------------------------------------
            sb_emu.init_ssh()
            sb_emu.build()

            # TEST run
            #-------------------------------------------------------------------

        except:
            pass

        finally:
            pass