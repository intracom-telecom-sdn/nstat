# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Orchestrator for active and idle tests
"""

import active_test
import argparse
import html_reporting as hr
import idle_test
import json
import logging
import os
import shutil
import util.plot_json as pj


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--test',
                        required=True,
                        type=str,
                        dest='test_type',
                        action='store',
                        help='Test type: {active,idle}')
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
    parser.add_argument('--gen-base-dir',
                        required=True,
                        type=str,
                        dest='gen_base_dir',
                        action='store',
                        help='Generator base directory')
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

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG,
                        filename=args.log_file,
                        format='[%(asctime)s %(levelname)7s ] %(message)s')

    # 01. parse configuration options from JSON
    logging.info('Parsing test configuration')
    jf = open(args.json_config)
    test_config = json.load(jf)

    # 02. run test
    if not args.bypass_test:
        logging.info('Running test {0}'.format(args.test_type))
        if args.test_type == 'active':
            active_test.active_test_run(
                args.json_output, args.ctrl_base_dir, args.gen_base_dir,
                test_config, args.output_dir)
        elif args.test_type == 'idle':
            idle_test.idle_test_run(
                args.json_output, args.ctrl_base_dir, args.gen_base_dir,
                test_config, args.output_dir)


    # 03. if results have been produced, generate plots, report and gather
    # output files
    if os.path.isfile(args.json_output):
        logging.info('Producing plots')
        num_plots = len(test_config['plots'])
        for i in range(0, num_plots):
            pj.plot_json(
                args.json_output,
                test_config['plots'][i]['x_axis_key'],
                test_config['plots'][i]['y_axis_key'],
                test_config['plots'][i]['z_axis_key'],
                test_config['plots'][i]['x_axis_label'],
                test_config['plots'][i]['y_axis_label'],
                test_config['plots'][i]['plot_type'],
                test_config['plots'][i]['plot_title'],
                test_config['plots'][i]['plot_subtitle_keys'],
                test_config['plots'][i]['plot_filename'] + '.png',
                xmin=test_config['plots'][i]['x_min'],
                xmax=test_config['plots'][i]['x_max'],
                ymin=test_config['plots'][i]['y_min'],
                ymax=test_config['plots'][i]['y_max'])

        logging.info('Generating html report')
        hr.generate_html(
            args.json_config, args.json_output, args.html_report,
            args.test_type)

        logging.info('Gathering all produced files into output directory')

        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)

        # move pngs, html report, log file, in and out json's to output dir
        for i in range(0, num_plots):
            shutil.move(test_config['plots'][i]['plot_filename'] + '.png',
                        args.output_dir)
        shutil.move(args.html_report, args.output_dir)
        if args.log_file:
            shutil.move(args.log_file, args.output_dir)
        shutil.copy(args.json_output, args.output_dir)
        shutil.copy(args.json_config, args.output_dir)
    else:
        logging.error('No output file {0} found. Finishing.'.\
            format(args.json_output))
