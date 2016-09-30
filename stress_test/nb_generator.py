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

class NBgen:

    def __init__(self, nb_gen_base_dir, test_config):

        """Create an NB-generator object. Options from JSON input file
        :param test_config: JSON input configuration
        :param nb_gen_base_dir: emulator base directory
        :type test_config: JSON configuration dictionary
        :type nb_gen_base_dir: str
        """
        self.base_dir = nb_gen_base_dir

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

        '''check handlers' validity'''


