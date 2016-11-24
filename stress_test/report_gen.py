# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import os
import stress_test.html_generation
import json
import logging
import shutil
import util.plot_json


class ReportGen:

    def __init__(self, args, test_config_json, total_samples, report_spec):
        """
        """
        self.test_config_json = test_config_json
        self.args = args
        self.report_spec = report_spec
        self.total_samples = total_samples
        try:
            logging.info('[ReportGen] creating test output directory if not '
                         'present.')
            if not os.path.exists(args.output_dir):
                os.mkdir(args.output_dir)
        except:
            logging.error(
                '[ReportGen] Fail to create output directory for the report')
            raise(IOError)

    def generate_json_results(self):
        """ Creates the result json file and writes test results in it

        :param results A list containing the results.
        :param out_json: The file path of json file to be created and write
        results in it
        :type results: <list<dictionary>>
        :type out_json: str
        """

        try:
            if len(self.total_samples) > 0:
                with open(self.args.json_output, 'w') as ojf:
                    json.dump(self.total_samples, ojf)
                    ojf.close()
                    logging.info(
                        '[generate_json_results] Results written to {0}.'.
                        format(self.args.json_output))
            else:
                logging.error(
                    '[generate_json_results] results parameter was empty.'
                    ' Nothing to be saved')
        except:
            logging.error(
                '[generate_json_results] output json file could not be '
                'created. Check privileges.')

    def generate_plots(self):
        """NSTAT post test actions

        :param args: argparse.ArgumentParser object containing user specified
        parameters (i.e test type, controller base directory, generator base
        directory) when running NSTAT
        :param test_config : JSON input configuration
        :param report_spec : A ReportSpec object that holds all the test report
        information and is passed as input to the generate_html() function in the
        html_generation.py, that is responsible for the report generation.
        :type args: ArgumentParser object
        :type test_config: python object resulting from a deserialized file like
        object containing a json document
        :type report_spec: ReportSpec object
        """

        if os.path.isfile(self.args.json_output):
            logging.info(
                '[nstat_orchestrator] Creating output directory of test results.')
            if not os.path.exists(self.args.output_dir):
                os.makedirs(self.args.output_dir)

            logging.info('[nstat_orchestrator] Producing plots')
            num_plots = len(self.test_config_json['plots'])
            for plot_index in list(range(0, num_plots)):
                try:
                    plot_options = util.plot_utils.PlotOptions()
                    plot_options.xmin = self.test_config_json['plots'][plot_index]['x_min']
                    plot_options.xmax = self.test_config_json['plots'][plot_index]['x_max']
                    plot_options.ymin = self.test_config_json['plots'][plot_index]['y_min']
                    plot_options.ymax = self.test_config_json['plots'][plot_index]['y_max']
                    plot_options.x_axis_label = \
                        self.test_config_json['plots'][plot_index]['x_axis_label']
                    plot_options.y_axis_label = \
                        self.test_config_json['plots'][plot_index]['y_axis_label']
                    plot_options.out_fig = \
                        self.test_config_json['plots'][plot_index]['plot_filename'] + '.png'
                    plot_options.plot_title = \
                        self.test_config_json['plots'][plot_index]['plot_title']
                    plot_options.x_axis_fct = \
                        float(eval(self.test_config_json['plots'][plot_index]['x_axis_factor']))
                    plot_options.y_axis_fct = \
                        float(eval(self.test_config_json['plots'][plot_index]['y_axis_factor']))
                    if self.test_config_json['plots'][plot_index]['x_axis_scale'] == 'log':
                        plot_options.xscale_log = True
                    else:
                        plot_options.xscale_log = False

                    if self.test_config_json['plots'][plot_index]['y_axis_scale'] == 'log':
                        plot_options.yscale_log = True
                    else:
                        plot_options.yscale_log = False
                    # Call the util function responsible to generate the plot png
                    util.plot_json.plot_json(
                        self.args.json_output,
                        self.test_config_json['plots'][plot_index]['x_axis_key'],
                        self.test_config_json['plots'][plot_index]['y_axis_key'],
                        self.test_config_json['plots'][plot_index]['z_axis_key'],
                        self.test_config_json['plots'][plot_index]['plot_type'],
                        self.test_config_json['plots'][plot_index]['plot_subtitle_keys'],
                        plot_options)
                    # Move produced plot in output directory
                    logging.info(
                        '[nstat_orchestrator] Gathering plot {0} into output '
                        'directory'.format(plot_options.out_fig))
                    shutil.move(plot_options.out_fig, self.args.output_dir)
                except:
                    logging.error(
                        '[nstat_orchestrator] The plot {0} could not be '
                        'created. Please check configuration. Continuing '
                        'to the next plot.'.
                        format(self.test_config_json['plots'][plot_index]['plot_title']))
        else:
            logging.error(
                '[nstat_orchestrator] No output file {0} found. Finishing.'.
                format(self.args.json_output))

    def save_controller_log(self):
        """NSTAT save log file
        :param args: argparse.ArgumentParser object containing user specified
        parameters (i.e test type, controller base directory, generator base
        directory) when running NSTAT
        :type args: ArgumentParser object
        """
        # Move controller log file if exist inside the test output dir
        try:
            logging.info('[save_controller_log] collecting logs')
            util.netutil.copy_dir_remote_to_local2(
                self.test_config_json.controller_node_ip,
                self.test_config_json.controller_node_ssh_port,
                self.test_config_json.controller_node_username,
                self.test_config_json.controller_node_password,
                self.test_config_json.controller_logs_dir,
                self.args.output_dir + '/log')
        except:
            logging.error('[save_controller_log] Fail transferring controller'
                          ' logs directory.')

    def generate_html_report(self):
        """NSTAT save log file
        :param args: argparse.ArgumentParser object containing user specified
        parameters (i.e test type, controller base directory, generator base
        directory) when running NSTAT
        :param report_spec: A ReportSpec object that holds all the test report
        information and is passed as input to the generate_html() function in the
        html_generation.py, that is responsible for the report generation.
        :type args: ArgumentParser object
        :type report_spec: ReportSpec object
        """
        # Generate html report and move it within test output dir
        logging.info('[nstat_orchestrator] Generating html report')
        stress_test.html_generation.generate_html(self.report_spec,
                                                  self.args.html_report)
        shutil.move(self.args.html_report, self.args.output_dir)
