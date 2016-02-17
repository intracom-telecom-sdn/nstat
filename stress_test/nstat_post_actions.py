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
import nb_active_scalability_mininet
import nb_active_scalability_multinet
import os
import sb_active_multinet_scalability
import sb_active_scalability_cbench
import sb_active_stability_cbench
import sb_idle_scalability_cbench
import sb_idle_scalability_mininet
import sb_idle_scalability_multinet
import sb_idle_stability_multinet
import shutil
import sys
import util.plot_json


def nstat_post_test_actions(args, test_config, report_spec):

    # 03. if results have been produced, generate plots, report and gather
    # output files
    if os.path.isfile(args.json_output):
        logging.info(
            '[nstat_orchestrator] Creating output directory of test results.')
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)

        logging.info('[nstat_orchestrator] Producing plots')
        num_plots = len(test_config['plots'])
        for plot_index in list(range(0, num_plots)):
            try:
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
                # Move produced plot in output directory
                logging.info(
                    '[nstat_orchestrator] Gathering plot {0} into output '
                    'directory'.format(plot_options.out_fig))
                shutil.move(plot_options.out_fig, args.output_dir)
            except:
                logging.error(
                    '[nstat_orchestrator] The plot {0} could not be created. '
                    'Please check configuration. Continuing to the next plot.'.
                    format(test_config['plots'][plot_index]['plot_title']))

        nstat_test_save_logfile(args)
        nstat_test_save_report(args, report_spec)

    else:
        logging.error(
            '[nstat_orchestrator] No output file {0} found. Finishing.'.
            format(args.json_output))

def nstat_test_save_logfile(args):

        # Move controller log file if exist inside the test output dir
        if args.log_file:
            shutil.move(args.log_file, args.output_dir)
        shutil.copy(args.json_output, args.output_dir)
        shutil.copy(args.json_config, args.output_dir)

def nstat_test_save_report(args, report_spec):

        # Generate html report and move it within test output dir
        logging.info('[nstat_orchestrator] Generating html report')
        html_generation.generate_html(report_spec, args.html_report)
        shutil.move(args.html_report, args.output_dir)