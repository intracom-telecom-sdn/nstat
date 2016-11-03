# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Controller Class- All controller-related functionality is here"""

import logging
import os
import time
import util.file_ops
import util.netutil
import util.process
import queue


class TestType:

    def __init__(self, ctrl_base_dir, test_config):

        """
        """
        self.name = test_config['controller_name']

    def load_test_conf(self):
        """
        """
        pass


    def set_log_level_test(self):
        """
        """
        pass

    def test_selector(self):
        """
        """

        # compose full test name = test_type + emulator


        # Run the test
        if args.test_type == 'sb_active_scalability_mtcbench':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] Running test {0}'.
                             format(args.test_type))
                sb_active_scalability_cbench.sb_active_scalability_cbench_run(
                    args.json_output,
                    args.ctrl_base_dir,
                    args.sb_gen_base_dir,
                    test_config,
                    args.output_dir)

    def __sb_idle_scalability_multinet_run(self):
        """
        """
    def __sb_idle_scalability_multinet_run(self):
        """
        """

