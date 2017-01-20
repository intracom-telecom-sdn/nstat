# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Controller Class- All controller-related functionality is here"""

import json
import logging
import stress_test.report_gen
import stress_test.report_spec_templates
import stress_test.test_run
import sys


class TestType:
    """
    Creates a TestType object
    """
    def __init__(self, args):
        """
        Initializes test type coming from args (user defined in cli),
        total_samples: list with dictionaries, every "sample" is a
        dictionary containing keys/values of results gathered at the end
        of every run within the for loop of every *_run function in
        TestRun class..
        """
        self.test_type = args.test_type
        self.total_samples = None
        self.test_report_template = \
            stress_test.report_spec_templates.TestReport(self.test_type,
                                                         args.json_config)

    def load_test_conf(self, args):
        """
        Loading test configuration for NSTAT experiment. Parsing \
            configuration options from JSON input file

        :param args: ArgumentParser object containing user specified \
            parameters (i.e test type, controller base directory, generator \
            base directory) when running NSTAT
        :returns: json_conf:
        :rtype: json_conf:  python object resulting from a deserialized file \
            like object containing a json document
        :type args: ArgumentParser object
        """

        with open(args.json_config) as conf_file:
            json_conf = json.load(conf_file)
        return json_conf

    def set_test_log_level(self, args):
        """
        Setting log level for NSTAT experiment

        :param args: ArgumentParser object containing user specified \
            parameters (i.e test type, controller base directory, generator \
            base directory) when running NSTAT
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
        Selects which test to run depending on the information coming from
        the args object. nstat_test_type_run variable contains information
        test_type + sb_emulator_name, necessary to select which test to run.
        """
        self.set_test_log_level(args)
        json_conf = self.load_test_conf(args)
        nstat_test_type_run = args.test_type + '_' + \
            json_conf['sb_emulator_name'].lower()

        # Create instance of TestRun and initialize controller
        if not args.bypass_test:
            nstat_test_run = stress_test.test_run.TestRun(args, json_conf,
                                                          nstat_test_type_run)

        # Run the test
        if nstat_test_type_run == 'sb_active_scalability_mtcbench':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] running test: {0}'.
                             format(nstat_test_type_run))
                self.total_samples = \
                    nstat_test_run.sb_active_scalability_mtcbench_run(
                        json_conf,
                        args.json_output,
                        args.output_dir)
            try:
                logging.info('[{0}] Generating results report.'.
                             format(self.test_type))
                report_spec = \
                    self.test_report_template.sb_active_scalability_mtcbench(
                        args.json_output)
                report_gen = stress_test.report_gen.ReportGen(
                    args, json_conf, report_spec, self.total_samples)
                report_gen.results_report()
            except:
                logging.error('[{0}] Fail to generate test report.'.
                              format(self.test_type))

        elif nstat_test_type_run == 'sb_active_stability_mtcbench':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] running test:{0}'.
                             format(nstat_test_type_run))
                self.total_samples = \
                    nstat_test_run.sb_active_stability_mtcbench_run(
                        json_conf,
                        args.json_output,
                        args.output_dir)
            try:
                logging.info('[{0}] Generating results report.'.
                             format(self.test_type))
                report_spec = \
                    self.test_report_template.sb_active_stability_mtcbench(
                        args.json_output)
                report_gen = stress_test.report_gen.ReportGen(
                    args, json_conf, report_spec, self.total_samples)
                report_gen.results_report()
            except:
                logging.error('[{0}] Fail to generate test report.'.
                              format(self.test_type))

        elif nstat_test_type_run == 'sb_active_scalability_multinet':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] running test: {0}'.
                             format(nstat_test_type_run))
                self.total_samples = \
                    nstat_test_run.sb_active_scalability_multinet_run(
                        json_conf,
                        args.json_output,
                        args.output_dir)
            try:
                logging.info('[{0}] Generating results report.'.
                             format(self.test_type))
                report_spec = \
                    self.test_report_template.sb_active_scalability_multinet(
                        args.json_output)
                report_gen = stress_test.report_gen.ReportGen(
                    args, json_conf, report_spec, self.total_samples)
                report_gen.results_report()
            except:
                logging.error('[{0}] Fail to generate test report.'.
                              format(self.test_type))

        elif nstat_test_type_run == 'sb_idle_scalability_mtcbench':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] running test: {0}'.
                             format(nstat_test_type_run))
                self.total_samples = \
                    nstat_test_run.sb_idle_scalability_mtcbench_run(
                        json_conf,
                        args.json_output,
                        args.output_dir)
            try:
                logging.info('[{0}] Generating results report.'.
                             format(self.test_type))
                report_spec = \
                    self.test_report_template.sb_idle_scalability_mtcbench(
                        args.json_output)
                report_gen = stress_test.report_gen.ReportGen(
                    args, json_conf, report_spec, self.total_samples)
                report_gen.results_report()
            except:
                logging.error('[{0}] Fail to generate test report.'.
                              format(self.test_type))

        elif nstat_test_type_run == 'sb_idle_scalability_multinet':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] running test: {0}'.
                             format(nstat_test_type_run))
                self.total_samples = \
                    nstat_test_run.sb_idle_scalability_multinet_run(
                        json_conf,
                        args.json_output,
                        args.output_dir)
            try:
                logging.info('[{0}] Generating results report.'.
                             format(self.test_type))
                report_spec = \
                    self.test_report_template.sb_idle_scalability_multinet(
                        args.json_output)
                report_gen = stress_test.report_gen.ReportGen(
                    args, json_conf, report_spec, self.total_samples)
                report_gen.results_report()
            except:
                logging.error('[{0}] Fail to generate test report.'.
                              format(self.test_type))
        elif nstat_test_type_run == 'sb_idle_stability_multinet':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] running test: {0}'.
                             format(nstat_test_type_run))
                self.total_samples = \
                    nstat_test_run.sb_idle_stability_multinet_run(
                        json_conf,
                        args.json_output,
                        args.output_dir)
            try:
                logging.info('[{0}] Generating results report.'.
                             format(self.test_type))
                report_spec = \
                    self.test_report_template.sb_idle_stability_multinet(
                        args.json_output)
                report_gen = stress_test.report_gen.ReportGen(
                    args, json_conf, report_spec, self.total_samples)
                report_gen.results_report()
            except:
                logging.error('[{0}] Fail to generate test report.'.
                              format(self.test_type))

        elif nstat_test_type_run == 'nb_active_scalability_multinet':
            if not args.bypass_test:
                logging.info('[nstat_orchestrator] running test: {0}'.
                             format(nstat_test_type_run))
                self.total_samples = \
                    nstat_test_run.nb_active_scalability_multinet_run(
                        json_conf,
                        args.json_output,
                        args.output_dir)
            try:
                logging.info('[{0}] Generating results report.'.
                             format(self.test_type))
                report_spec = \
                    self.test_report_template.nb_active_scalability_multinet(
                        args.json_output)
                report_gen = stress_test.report_gen.ReportGen(
                    args, json_conf, report_spec, self.total_samples)
                report_gen.results_report()
            except:
                logging.error('[{0}] Fail to generate test report.'.
                              format(self.test_type))
        else:
            logging.error('[nstat_orchestrator] not valid test configuration')
            exit(0)
