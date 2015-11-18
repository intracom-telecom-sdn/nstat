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
import nb_active_mininet_remote
import os
import sb_active_cbench
import sb_idle_cbench
import sb_idle_mininet
import shutil
import sys
import util.plot_json


def main():
    """This is the main function where the main test application starts.
    """

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--test',
                        required=True,
                        type=str,
                        dest='test_type',
                        action='store',
                        help="sb_active_scalability_cbench \n"
                             "sb_active_scalability_mtcbench \n"
                             "sb_active_stability_cbench\n"
                             "sb_active_stability_mtcbench\n"
                             "sb_idle_scalability_cbench\n"
                             "sb_idle_scalability_mtcbench\n"
                             "sb_idle_scalability_mininet\n"
                             "nb_active_scalability_mininet")
    parser.add_argument('--bypass-execution',
                        dest='bypass_test',
                        action='store_true',
                        default=False,
                        help=('Bypass test execution and proceed to report '
                              'generation, based on a previous output.'))
    parser.add_argument('--ctrl-base-dir',
                        required=True,
                        type=str,
                        dest='ctrl_base_dir',
                        action='store',
                        help='Controller base directory')
    parser.add_argument('--sb-generator-base-dir',
                        required=True,
                        type=str,
                        dest='sb_gen_base_dir',
                        action='store',
                        help='Cbench or Mininet generator base directory')
    parser.add_argument('--nb-generator-base-dir',
                        required=False,
                        type=str,
                        dest='nb_gen_base_dir',
                        action='store',
                        help='Northbound traffic generator base directory')
    parser.add_argument('--json-config',
                        required=True,
                        type=str,
                        dest='json_config',
                        action='store',
                        help='Test configuration file (JSON)')
    parser.add_argument('--json-output',
                        required=True,
                        type=str,
                        dest='json_output',
                        action='store',
                        help='Output JSON file')
    parser.add_argument('--html-report',
                        required=True,
                        type=str,
                        dest='html_report',
                        action='store',
                        help='Generated HTML report file')
    parser.add_argument('--log-file',
                        dest='log_file',
                        action='store',
                        help='File to keep test logs')
    parser.add_argument('--output-dir',
                        required=True,
                        type=str,
                        dest='output_dir',
                        action='store',
                        help='Output directory to store produced files')
    parser.add_argument('--logging-level',
                        type=str,
                        dest='logging_level',
                        action='store',
                        default='DEBUG',
                        help="Setting the level of the logging messages."
                             "Can have one of the following values:\n"
                             "INFO\n"
                             "DEBUG (default)\n"
                             "ERROR")

    args = parser.parse_args()

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

    # 01. parse configuration options from JSON
    logging.info('[nstat_orchestrator] Parsing test configuration')
    json_conf_file = open(args.json_config)
    test_config = json.load(json_conf_file)

    # 02. run test

    # sb_active_cbench
    if args.test_type == 'sb_active_scalability_cbench'   or \
       args.test_type == 'sb_active_scalability_mtcbench' or \
       args.test_type == 'sb_active_stability_cbench'     or \
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
    elif args.test_type == 'sb_idle_scalability_cbench' or  \
         args.test_type == 'sb_idle_scalability_mtcbench':

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
            nb_active_mininet_remote.nb_active_mininet_run(args.json_output,
                                                    args.ctrl_base_dir,
                                                    args.nb_gen_base_dir,
                                                    args.sb_gen_base_dir,
                                                    test_config,
                                                    args.output_dir,
                                                    args.logging_level)
        report_spec = nb_active_mininet_remote.get_report_spec(args.test_type,
                                                        args.json_config,
                                                        args.json_output)
    else:
        logging.error('[nstat_orchestrator] not valid test configuration')
        exit(0)

    # 03. if results have been produced, generate plots, report and gather
    # output files
    if os.path.isfile(args.json_output):
        logging.info('[nstat_orchestrator] Producing plots')
        num_plots = len(test_config['plots'])
        for plot_index in list(range(0, num_plots)):
            plot_options = util.plot_utils.PlotOptions()
            plot_options.xmin = test_config['plots'][plot_index]['x_min']
            plot_options.xmax = test_config['plots'][plot_index]['x_max']
            plot_options.ymin = test_config['plots'][plot_index]['y_min']
            plot_options.ymax = test_config['plots'][plot_index]['y_max']
            plot_options.x_axis_label = \
                test_config['plots'][plot_index]['x_axis_label']
            plot_options.y_axis_label = \
                test_config['plots'][plot_index]['y_axis_label']
            plot_options.out_fig = \
                test_config['plots'][plot_index]['plot_filename'] + '.png'
            plot_options.plot_title = \
                test_config['plots'][plot_index]['plot_title']
            plot_options.x_axis_fct = \
                float(eval(test_config['plots'][plot_index]['x_axis_factor']))
            plot_options.y_axis_fct = \
                float(eval(test_config['plots'][plot_index]['y_axis_factor']))
            if test_config['plots'][plot_index]['x_axis_scale'] == 'log':
                plot_options.xscale_log = True
            else:
                plot_options.xscale_log = False

            if test_config['plots'][plot_index]['y_axis_scale'] == 'log':
                plot_options.yscale_log = True
            else:
                plot_options.yscale_log = False
            # Call the util function responsible to generate the plot png
            util.plot_json.plot_json(
                args.json_output,
                test_config['plots'][plot_index]['x_axis_key'],
                test_config['plots'][plot_index]['y_axis_key'],
                test_config['plots'][plot_index]['z_axis_key'],
                test_config['plots'][plot_index]['plot_type'],
                test_config['plots'][plot_index]['plot_subtitle_keys'],
                plot_options)

        logging.info(
            '[nstat_orchestrator] Creating output directory of test results.')
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)

        # move pngs, html report, log file, in and out json's to output dir
        logging.info(
            '[nstat_orchestrator] Gathering all produced files into output '
            'directory')
        for i in range(0, num_plots):
            shutil.move(test_config['plots'][i]['plot_filename'] + '.png',
                        args.output_dir)
        # Move controller log file if exist inside the test output dir
        if args.log_file:
            shutil.move(args.log_file, args.output_dir)
        shutil.copy(args.json_output, args.output_dir)
        shutil.copy(args.json_config, args.output_dir)
        # Generate html report and move it inside test output dir
        logging.info('[nstat_orchestrator] Generating html report')
        html_generation.generate_html(report_spec, args.html_report)
        shutil.move(args.html_report, args.output_dir)
    else:
        logging.error(
            '[nstat_orchestrator] No output file {0} found. Finishing.'.
            format(args.json_output))


if __name__ == '__main__':
    main()
