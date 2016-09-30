# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NB-Generator Class- All NB-Generator-related functionality is here"""

import json
import logging
import os
import re
import util.netutil


class NBgen:

    def __init__(self, nb_gen_base_dir, test_config):

        """Create an NB-generator object. Options from JSON input file
        :param test_config: JSON input configuration
        :param nb_gen_base_dir: emulator base directory
        :type test_config: JSON configuration dictionary
        :type nb_gen_base_dir: str
        """

        self.name = test_config['nb_generator_name']
        self.base_dir = nb_gen_base_dir

        self.cpus = test_config['nb_generator_cpu_shares']
        # self.host_spec = test_config['nb_generator_node_spec']
        # self.host_ip = test_config['nb_generator_host_ip']

        self.ip = test_config['nb_generator_ode_ip']
        self.ssh_port = test_config['nb_generator_node_ssh_port']
        self.ssh_user = test_config['nb_generator_node_username']
        self.ssh_pass = test_config['nb_generator_node_password']

        self.run_hnd = (self.base_dir +
                        test_config['nb_generator_run_handler'])
        self.status = 'UNKNOWN'
        self._ssh_conn = None

        self.flow_delete_flag = test_config['flow_delete_flag']
        self.flows_per_request = test_config['flows_per_request']
        self.log_level

        # The parameters initialized as None are dimensions of the test.
        # These values are passed outside, from the test in the main for loop.
        # ---------------------------------------------------------------------
        self.flow_workers = None
        self.total_flows = None
        self.flow_operations_delay_ms = None
        # ---------------------------------------------------------------------

    def init_ssh(self):
        logging.info(
            '[open_ssh_connection] Initiating SSH session with {0} node.'.
            format(self.name, self.ip))

        self._ssh_conn = util.netutil.ssh_connect_or_return2(self.ip,
                                                             int(self.ssh_port),
                                                             self.ssh_user,
                                                             self.ssh_pass,
                                                             10)

    def run(self, cntrl_ip, restconf_port, restconf_user, restconf_pass):
        logging.info("[NB_generator] Run handler")
        cmd = ('cd {0}; taskset -c {1} python3.4 {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12}'.
               format(self.base_dir,
                      self.cpus,
                      self.run_hnd,
                      cntrl_ip,
                      restconf_port,
                      self.total_flows,
                      self.flow_workers,
                      self.flow_operations_delay_ms,
                      self.flow_delete_flag,
                      restconf_user,
                      restconf_pass,
                      self.flows_per_request,
                      self.log_level))
        logging.debug('Generator handler command:{0}.'.format(cmd))

        exit_status, output = util.netutil.ssh_run_command(self._ssh_conn,
                                                           cmd,
                                                           '[NB_generator_run_handler]')
        if exit_status == 0:
            self.status = 'RUNNING'
            logging.info("[NB_generator] Successful started")
        else:
            self.status = 'NOT_RUNNING'
            raise Exception('[NB_generator] Failure during starting')
