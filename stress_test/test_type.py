# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Controller Class- All controller-related functionality is here"""

import json
import logging
import os
import time
import stress_test.controller
import stress_test.emulator
import sys
import util.file_ops
import util.netutil
import util.process
import queue



class TestType:

    def __init__(self, args):

        """
        """
        self.nstat_test_type = args.test_type


    def load_test_conf(self, args):
        """ Loading test configuration for NSTAT experiment. Parsing
        configuration options from JSON input file

        :param args: ArgumentParser object containing user specified
        parameters (i.e test type, controller base directory, generator base
        directory) when running NSTAT
        :returns: test_config:
        :rtype: test_config:  python object resulting from a deserialized file
        like object containing a json document
        :type args: ArgumentParser object
        """
        json_conf = {}
        with open(args.json_config) as conf_file:
            json_conf = json.load(conf_file)

            ctrl_base_dir = args.ctrl_base_dir
            sb_emu_base_dir = args.sb_emu_base_dir

            controller = stress_test.controller.Controller.new(ctrl_base_dir,
                                                               json_conf)
            sb_emulator = stress_test.emulator.SBEmu.new(sb_emu_base_dir,
                                                         json_conf)

            if hasattr(args, 'nb_emu_base_dir'):
                nb_emu_base_dir = args.nb_emu_base_dir
                nb_emulator = stress_test.emulator.SBEmu.new(nb_emu_base_dir,
                                                             json_conf)

    def set_test_log_level(self, args):
        """Setting log level for NSTAT experiment

        :param args: ArgumentParser object containing user specified
        parameters (i.e test type, controller base directory, generator base
        directory) when running NSTAT
        :type args: ArgumentParser object
        """
        logging_format = '[%(asctime)s %(levelname)7s ] %(message)s'
        if args.logging_level == 'INFO':
            logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                            format=logging_format)
        elif args.logging_level == 'ERROR':
            logging.basicConfig(level=logging.ERROR, stream=sys.stdout,
                            format=logging_format)
        else:
            logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                            format=logging_format)

        if args.log_file:
            open(args.log_file, 'a').close()
            file_logging_handler = logging.FileHandler(filename=args.log_file,
                                                       mode='w')
            if args.logging_level == 'INFO':
                file_logging_handler.setLevel(level=logging.INFO)
            elif args.logging_level == 'ERROR':
                file_logging_handler.setLevel(level=logging.ERROR)
            else:
                file_logging_handler.setLevel(level=logging.DEBUG)


    def test_selector(self, args):
        """
        """
        self.set_test_log_level(args)
        self.load_test_conf(args)
        exit()
        # compose full NSTAT test type depending on cli argument test_type and
        # emulator type
        emulator_name
        nstat_test_type = args.test_type + args.emulator_name

        # Run the test
        if nstat_test_type == 'sb_active_scalability_mtcbench':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] Running test {0}'.
                             format(nstat_test_type))
                exit()
                sb_active_scalability_cbench.sb_active_scalability_cbench_run(
                    args.json_output,
                    args.ctrl_base_dir,
                    args.sb_gen_base_dir,
                    test_config,
                    args.output_dir)

        # sb_active_stability_mtcbench
        elif nstat_test_type == 'sb_active_stability_mtcbench':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] Running test {0}'.
                             format(nstat_test_type))
                exit()
                sb_active_stability_cbench.sb_active_stability_cbench_run(
                    args.json_output,
                    args.ctrl_base_dir,
                    args.sb_gen_base_dir,
                    test_config,
                    args.output_dir)

        elif nstat_test_type == 'sb_active_scalability_multinet':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] Running test {0}'.
                             format(nstat_test_type))
                exit()
                oftraf_path = get_oftraf_path()
                sb_active_scalability_multinet.sb_active_scalability_multinet_run(
                    args.json_output,
                    args.ctrl_base_dir,
                    args.sb_gen_base_dir,
                    test_config,
                    args.output_dir,
                    oftraf_path)

        elif nstat_test_type == 'sb_idle_scalability_mtcbench':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] Running test {0}'.
                             format(nstat_test_type))
                exit()
                sb_idle_scalability_cbench.sb_idle_scalability_cbench_run(
                    args.json_output,
                    args.ctrl_base_dir,
                    args.sb_gen_base_dir,
                    test_config,
                    args.output_dir)

        elif nstat_test_type == 'sb_idle_scalability_multinet':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] Running test {0}'.
                             format(nstat_test_type))
                exit()
                sb_idle_scalability_multinet.sb_idle_scalability_multinet_run(
                    args.json_output,
                    args.ctrl_base_dir,
                    args.sb_gen_base_dir,
                    test_config,
                    args.output_dir)

        elif nstat_test_type == 'sb_idle_stability_multinet':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] Running test {0}'.
                             format(nstat_test_type))
                exit()
                oftraf_path = get_oftraf_path()
                sb_idle_stability_multinet.sb_idle_stability_multinet_run(
                    args.json_output,
                    args.ctrl_base_dir,
                    args.sb_gen_base_dir,
                    test_config,
                    args.output_dir,
                    oftraf_path)

        elif nstat_test_type == 'nb_active_scalability_multinet':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] Running test {0}'.
                             format(nstat_test_type))
                exit()
                nb_active_scalability_multinet.nb_active_scalability_multinet_run(
                    args.json_output,
                    args.ctrl_base_dir,
                    args.nb_gen_base_dir,
                    args.sb_gen_base_dir,
                    test_config,
                    args.output_dir,
                    args.logging_level)

        else:
            logging.error('[nstat_orchestrator] not valid test configuration')
            exit(0)

