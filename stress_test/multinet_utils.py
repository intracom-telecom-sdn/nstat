# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Multinet-related utilities
"""


import logging
import os
import util.customsubprocess


MULTINET_BASE_DIR = ('{0}/emulators/multinet'.
    format(os.path.dirname(os.path.realpath(__file__))))

def multinet_command_runner(exec_path, logging_prefix, is_privileged=False):
    """
    General wrapper for running multinet handlers and deploy/cleanup multinet
    scripts

    :param exec_path: the full path of handler or script to be executed
    :param logging_prefix: the logging message prefix
    :param is_privileged: flag to indicate if the executed script or handler
    will be executed in privileged mode
    :type exec_path: str
    :type logging_prefix: str
    :type is_privileged: bool
    """

    run_cmd_prefix = ''
    if is_privileged:
        run_cmd_prefix = 'sudo'
    multinet_run_cmd = ('{0} PYTHONPATH={1} python {2} --json-config {3}'.
                            format(run_cmd_prefix, MULTINET_BASE_DIR,
                                   exec_path,
                                   MULTINET_BASE_DIR + '/config/config.json'))
    logging.debug('[{0}] multinet command to run: {1}'.
                  format(logging_prefix, multinet_run_cmd))
    util.customsubprocess.check_output_streaming(multinet_run_cmd,
                                                 '[{0}]'.format(logging_prefix))


def generate_multinet_config(controller_sb_interface, multinet_rest_server,
                             multinet_size, multinet_group_size,
                             multinet_group_delay_ms, multinet_hosts_per_switch,
                             multinet_topology_type):
    pass

