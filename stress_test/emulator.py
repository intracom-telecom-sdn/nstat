# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" SB-Emulator Class- All SB-Emulator-related functionality is here"""

import json
import logging
import os
import util


class SBEmu:

    def __init__(self, sb_emu_base_dir, test_config):

        """Create an SB-Emulator object. Options from JSON input file
        :param test_config: JSON input configuration
        :param sb_emu_base_dir: emuulator base directory
        :type test_config: JSON configuration dictionary
        :type sb_emu_base_dir: str
        """
        self.name = test_config['SB-Emulator_name']
        self.base_dir = sb_emu_base_dir

        self.host_spec = test_config['SB-Emulator_node_spec']
        self.host_ip = test_config['SB-Emulator_host_ip']

        self.ip = test_config['SB-Emulator_node_ip']
        self.ssh_port = test_config['SB-Emulator_node_ssh_port']
        self.ssh_user = test_config['SB-Emulator_node_username']
        self.ssh_pass = test_config['SB-Emulator_node_password']

        self.build_hnd = self.base_dir + test_config['SB-Emulator_build_handler']
        self.clean_hnd = self.base_dir + test_config['SB-Emulator_clean_handler']

        self.status = 'UNKNOWN'
        self._ssh_conn = None

        '''check handlers' validity'''
        util.file_ops.check_filelist([self.build_hnd,
                                      self.clean_hnd])


class MTCBench(SBEmu):

    def __init__(self, sb_emu_base_dir, test_config):

        super(self.__class__, self).__init__(sb_emu_base_dir, test_config)

        self.need_rebuild = test_config['mtcbench_rebuild']
        self.need_cleanup = test_config['mtcbench_cleanup']

        self.run_hnd = self.base_dir + test_config['mtcbench_run_handler']

        self.simulated_hosts = test_config['mtcbench_simulated_hosts']
        self.switches_per_thread = test_config['mtcbench_switches_per_thread']
        self.threads = test_config['mtcbench_threads']
        self.thread_creation_delay_ms = test_config['mtcbench_thread_creation_delay_ms']
        self.delay_before_traffic_ms = test_config['mtcbench_delay_before_traffic_ms']
        self.mode = test_config['mtcbench_mode']
        self.warmup = test_config['mtcbench_warmup']
        self.ms_per_test = test_config['mtcbench_ms_per_test']
        self.internal_repeats = test_config['mtcbench_internal_repeats']
        self.cpu_shares = test_config['mtcbench_cpu_shares']


class Multinet(SBEmu):

    def __init__(self, sb_emu_base_dir, test_config):

        super(self.__class__, self).__init__(sb_emu_base_dir, test_config)

        self.rest_server_boot = test_config['topology_rest_server_boot']
        self.rest_server_stop = test_config['topology_rest_server_stop']
        self.rest_server_port = test_config['topology_rest_server_port']

        self.init_handler = test_config['topology_init_handler']
        self.start_switches_handler = test_config['topology_start_switches_handler']
        self.stop_switches_handler = test_config['topology_stop_switches_handler']
        self.get_switches_handler = test_config['topology_get_switches_handler']
        self.traffic_gen_handler = test_config['topology_traffic_gen_handler']

        self.topo_size = ['multinet_topo_size']
        self.topo_type = test_config['multinet_topo_type']
        self.topo_hosts_per_switch = test_config['multinet_topo_hosts_per_switch']
        self.topo_group_size = test_config['multinet_topo_group_size']
        self.topo_group_delay_ms = test_config['multinet_topo_group_delay_ms']

        self.traffic_generation_duration_ms = test_config['']
        self.interpacket_delay_ms = test_config['']

        self.multinet_switch_type = test_config['multinet_switch_type']
        self.multinet_worker_ip_list = test_config['multinet_worker_ip_list']
        self.multinet_worker_port_list = test_config['multinet_worker_port_list']


        def generate_multinet_config(self, cntrl_of_port, cntrl_ip):
            """
            Generates a new json configuration file for multinet, according to the
            configuration values that are passed as parameters.
            """

            config_data = {}
            # Path where configuration of Multinet will be saved
            multinet_config_file_path = '{0}/config.json'.format(self.base_dir)


            config_data['master_ip'] = self.ip
            config_data['master_port'] = self.rest_server_port
            config_data['worker_ip_list'] = self.multinet_worker_ip_list
            config_data['worker_port_list'] = self.multinet_worker_port_list
            config_data['deploy']['multinet_base_dir'] = self.base_dir
            config_data['deploy']['ssh_port'] = self.ssh_port
            config_data['deploy']['username'] = self.ssh_user
            config_data['deploy']['password'] = self.ssh_pass
            config_data['topo']['controller_ip_address'] = cntrl_ip
            config_data['topo']['controller_of_port'] = cntrl_of_port
            config_data['topo']['switch_type'] = self.multinet_switch_type
            config_data['topo']['topo_type'] = self.topo_type
            config_data['topo']['topo_size'] = self.topo_size
            config_data['topo']['group_size'] = self.topo_group_size
            config_data['topo']['group_delay'] = self.topo_group_delay_ms
            config_data['topo']['hosts_per_switch'] = self.topo_hosts_per_switch
            config_data['topo']['traffic_generation_duration_ms'] = self.traffic_generation_duration_ms
            config_data['topo']['interpacket_delay_ms'] = self.interpacket_delay_ms

            with open(multinet_config_file_path, 'w') as config_json_file:
                json.dump(config_data, config_json_file)
            if not os.path.isfile(multinet_config_file_path):
                raise IOError("Multinet JSON configuration file could not be created.")


    @staticmethod
    def new(sb_emu_base_dir, test_config):
        """ Factory method. Creates a subclass class depending on the
        SB-Emulator name
        :returns: a subclass or None
        :rtype: object
        """
        name = test_config['SB-Emulator_name']
        if (name == 'MTCBench'):
            return MTCBench(sb_emu_base_dir, test_config)
        elif (name == 'Multinet'):
            return Multinet(sb_emu_base_dir, test_config)
        else:
            raise NotImplementedError('Not supported yet')

    def init_ssh(self):
        logging.info(
            '[open_ssh_connection] Initiating SSH session with {0} node.'.
            format(self.name, self.ip))

        self._ssh_conn = util.netutil.ssh_connect_or_return2(self.ip,
                                                             int(self.ssh_port),
                                                             self.ssh_user,
                                                             self.ssh_pass,
                                                             10)

    def build(self):
        """ Wrapper to the SB-Emulator build handler
        """
        logging.info('[SB-Emulator] Building')
        self.status = 'BUILDING'

        exit_status = util.netutil.ssh_run_command(self._ssh_conn,
                                                   ' '.join([self.build_hnd]),
                                                   '[SB-Emulator.'
                                                   'build_handler]')[0]
        if exit_status == 0:
            self.status = 'BUILT'
            logging.info("[SB-Emulator] Successful building")
        else:
            self.status = 'NOT BUILT'
            logging.error("[SB-Emulator] Failure during building")
            raise Exception('[SB-Emulator] Failure during building')

    def cleanup(self):
        """Wrapper to the SB-Emulator cleanup handler
        """
        logging.info('[SB-Emulator] Cleaning up')

        self.status = 'CLEANING'
        util.netutil.ssh_run_command(self._ssh_conn,
                                     self.clean_hnd,
                                     '[SB-Emulator.clean_handler]')[0]
        self.status = 'CLEANED'
