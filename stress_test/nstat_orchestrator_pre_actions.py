# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html



"""
Orchestrator for stress tests.
"""

import argparse
import html_generation
import json
import logging
import nb_active_mininet
import os
import sb_active_cbench
import sb_idle_cbench
import sb_idle_mininet
import shutil
import sys
import util.plot_json


def nstat_test_set_log_level(args):

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

def nstat_load_test_conf(args):

    # 01. parse configuration options from JSON
    logging.info('[nstat_orchestrator] Parsing test configuration')
    json_conf_file = open(args.json_config)
    test_config = json.load(json_conf_file)

def nstat_test_selector(args):

    # sb_active_cbench
    if args.test_type == 'sb_active_scalability_mtcbench' or \
       args.test_type == 'sb_active_stability_mtcbench':

        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            sb_active_cbench.sb_active_cbench_run(args.json_output,
                                                  args.ctrl_base_dir,
                                                  args.sb_gen_base_dir,
                                                  test_config,
                                                  args.output_dir)
        report_spec = sb_active_cbench.get_report_spec(args.test_type,
                                                       args.json_config,
                                                       args.json_output)

    # sb_idle_cbench
    elif args.test_type == 'sb_idle_scalability_mtcbench':

        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            sb_idle_cbench.sb_idle_cbench_run(
                args.json_output,
                args.ctrl_base_dir,
                args.sb_gen_base_dir,
                test_config,
                args.output_dir)
        report_spec = sb_idle_cbench.get_report_spec(args.test_type,
                                                     args.json_config,
                                                     args.json_output)

    # sb_idle_mininet
    elif args.test_type == 'sb_idle_scalability_mininet':

        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            sb_idle_mininet.sb_idle_mininet_run(args.json_output,
                                                args.ctrl_base_dir,
                                                args.sb_gen_base_dir,
                                                test_config,
                                                args.output_dir)
        report_spec = sb_idle_mininet.get_report_spec(args.test_type,
                                                      args.json_config,
                                                      args.json_output)
    # sb_active_mininet
    elif args.test_type == 'nb_active_scalability_mininet':

        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            nb_active_mininet.nb_active_mininet_run(args.json_output,
                                                    args.ctrl_base_dir,
                                                    args.nb_gen_base_dir,
                                                    args.sb_gen_base_dir,
                                                    test_config,
                                                    args.output_dir,
                                                    args.logging_level)
        report_spec = nb_active_mininet.get_report_spec(args.test_type,
                                                        args.json_config,
                                                        args.json_output)
    else:
        logging.error('[nstat_orchestrator] not valid test configuration')
        exit(0)

