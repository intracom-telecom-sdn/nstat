# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
"""
Orchestrator for stress tests.
"""

import json
import logging
import nb_active_scalability_mininet
import nb_active_scalability_multinet
import os
import sb_active_scalability_cbench
import sb_active_scalability_multinet
import sb_active_stability_cbench
import sb_idle_scalability_cbench
import sb_idle_scalability_mininet
import sb_idle_scalability_multinet
import sb_idle_stability_multinet
import sys


def nstat_test_set_log_level(args):
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

def nstat_load_test_conf(args):
    """Loading test configuration for NSTAT experiment. Parsing configuration
    options from JSON input file

    :param args: ArgumentParser object containing user specified
    parameters (i.e test type, controller base directory, generator base
    directory) when running NSTAT
    :returns: test_config:
    :rtype: test_config:  python object resulting from a deserialized file like
    object containing a json document
    :type args: ArgumentParser object
    """

    logging.info('[nstat_orchestrator] Parsing test configuration')
    json_conf_file = open(args.json_config)
    test_config = json.load(json_conf_file)
    return test_config

def nstat_test_selector(args, test_config):
    """NSTAT test selector: depending on the test_type defined on the command
    line options of NSTAT

    :param args: ArgumentParser object containing user specified
    parameters (i.e test type, controller base directory, generator base
    directory) when running NSTAT
    :param test_config: JSON input configuration
    :returns: report_spec: A ReportSpec object that holds all the test report
    information and is passed as input to the generate_html() function in the
    html_generation.py, that is responsible for the report generation.
    :rtype: report_spec: ReportSpec object
    :type args: ArgumentParser object
    :type test_config: JSON configuration dictionary
    """
    # sb_active_scalability_mtcbench
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

        report_spec = sb_active_scalability_cbench.get_report_spec(
            args.test_type,
            args.json_config,
            args.json_output)

    # sb_active_stability_mtcbench
    elif args.test_type == 'sb_active_stability_mtcbench':
        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            sb_active_stability_cbench.sb_active_stability_cbench_run(
                args.json_output,
                args.ctrl_base_dir,
                args.sb_gen_base_dir,
                test_config,
                args.output_dir)

        report_spec = sb_active_stability_cbench.get_report_spec(
            args.test_type,
            args.json_config,
            args.json_output)

    elif args.test_type == 'sb_active_scalability_multinet':
        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            oftraf_path = get_oftraf_path()
            sb_active_scalability_multinet.sb_active_scalability_multinet_run(
                args.json_output,
                args.ctrl_base_dir,
                args.sb_gen_base_dir,
                test_config,
                args.output_dir,
                oftraf_path)

        report_spec = sb_active_scalability_multinet.get_report_spec(
            args.test_type,
            args.json_config,
            args.json_output)

    # sb_idle_scalability_mtcbench
    elif args.test_type == 'sb_idle_scalability_mtcbench':

        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            sb_idle_scalability_cbench.sb_idle_scalability_cbench_run(
                args.json_output,
                args.ctrl_base_dir,
                args.sb_gen_base_dir,
                test_config,
                args.output_dir)

        report_spec = sb_idle_scalability_cbench.get_report_spec(
            args.test_type,
            args.json_config,
            args.json_output)

    # sb_idle_scalability_mininet
    elif args.test_type == 'sb_idle_scalability_mininet':

        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            sb_idle_scalability_mininet.sb_idle_scalability_mininet_run(
                args.json_output,
                args.ctrl_base_dir,
                args.sb_gen_base_dir,
                test_config,
                args.output_dir)

        report_spec = sb_idle_scalability_mininet.get_report_spec(
            args.test_type,
            args.json_config,
            args.json_output)

    # sb_idle_scalability_multinet
    elif args.test_type == 'sb_idle_scalability_multinet':

        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            sb_idle_scalability_multinet.sb_idle_scalability_multinet_run(
                args.json_output,
                args.ctrl_base_dir,
                args.sb_gen_base_dir,
                test_config,
                args.output_dir)

        report_spec = sb_idle_scalability_multinet.get_report_spec(
            args.test_type,
            args.json_config,
            args.json_output)

    # sb_idle_stability_multinet
    elif args.test_type == 'sb_idle_stability_multinet':

        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            oftraf_path = get_oftraf_path()
            sb_idle_stability_multinet.sb_idle_stability_multinet_run(
                args.json_output,
                args.ctrl_base_dir,
                args.sb_gen_base_dir,
                test_config,
                args.output_dir,
                oftraf_path)

        report_spec = sb_idle_stability_multinet.get_report_spec(
            args.test_type,
            args.json_config,
            args.json_output)

    # nb_active_scalability_mininet
    elif args.test_type == 'nb_active_scalability_mininet':

        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            nb_active_scalability_mininet.nb_active_scalability_mininet_run(
                args.json_output,
                args.ctrl_base_dir,
                args.nb_gen_base_dir,
                args.sb_gen_base_dir,
                test_config,
                args.output_dir,
                args.logging_level)

        report_spec = nb_active_scalability_mininet.get_report_spec(
            args.test_type,
            args.json_config,
            args.json_output)

    # nb_active_scalability_multinet
    elif args.test_type == 'nb_active_scalability_multinet':

        if not args.bypass_test:
            logging.info('[nstat_orchestrator] Running test {0}'.
                         format(args.test_type))
            nb_active_scalability_multinet.nb_active_scalability_multinet_run(
                args.json_output,
                args.ctrl_base_dir,
                args.nb_gen_base_dir,
                args.sb_gen_base_dir,
                test_config,
                args.output_dir,
                args.logging_level)

        report_spec = nb_active_scalability_multinet.get_report_spec(
            args.test_type,
            args.json_config,
            args.json_output)
    else:
        logging.error('[nstat_orchestrator] not valid test configuration')
        exit(0)

    return report_spec

def get_oftraf_path():
    """Returns oftraf base directory path relatively to the project path
    """
    stress_test_base_dir = os.path.abspath(os.path.join(
        os.path.realpath(__file__), os.pardir))
    monitors_base_dir = os.path.abspath(os.path.join(stress_test_base_dir,
                                                    os.pardir))
    oftraf_path = os.path.sep.join(
        [monitors_base_dir, 'monitors', 'oftraf', ''])
    return oftraf_path
