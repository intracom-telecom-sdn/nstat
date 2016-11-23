# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" SB-Emulator Class- All SB-Emulator-related functionality is here"""

import json
import logging
import os
import re
import util.netutil
import util.file_ops


class SBEmu:

    def __init__(self, sb_emu_base_dir, test_config):

        """Create an SB-Emulator object. Options from JSON input file
        :param test_config: JSON input configuration
        :param sb_emu_base_dir: emulator base directory
        :type test_config: JSON configuration dictionary
        :type sb_emu_base_dir: str
        """
        self.name = test_config['sb_emulator_name']
        self.base_dir = sb_emu_base_dir

        # self.host_spec = test_config['SB-Emulator_node_spec']
        # self.host_ip = test_config['SB-Emulator_host_ip']

        self.ip = test_config['sb_emulator_node_ip']
        self.ssh_port = test_config['sb_emulator_node_ssh_port']
        self.ssh_user = test_config['sb_emulator_node_username']
        self.ssh_pass = test_config['sb_emulator_node_password']

        self.build_hnd = (self.base_dir +
                          test_config['sb_emulator_build_handler'])
        self.clean_hnd = (self.base_dir +
                          test_config['sb_emulator_clean_handler'])
        self.status = 'UNKNOWN'
        self._ssh_conn = None

        '''check handlers' validity'''
        util.file_ops.check_filelist([self.build_hnd,
                                      self.clean_hnd])

    @staticmethod
    def new(sb_emu_base_dir, test_config):
        """ Factory method. Creates a subclass class depending on the
        SB-Emulator name
        :returns: a subclass or None
        :rtype: object
        """
        name = test_config['sb_emulator_name']
        if (name == 'MTCBENCH'):
            return MTCBench(sb_emu_base_dir, test_config)
        elif (name == 'MULTINET'):
            return Multinet(sb_emu_base_dir, test_config)
        else:
            raise NotImplementedError('Not supported yet')

    def init_ssh(self):
        """Initializes a new SSH client object, with the emulator node and
        stores it to the protected variable _ssh_conn. If a connection already
        exists it returns a new SSH client object to the emulator node.
        """
        logging.info(
            '[open_ssh_connection] Initiating SSH session with {0} node.'.
            format(self.name, self.ip))
        if self._ssh_conn is None:
            self._ssh_conn = \
                util.netutil.ssh_connect_or_return2(self.ip,
                                                    int(self.ssh_port),
                                                    self.ssh_user,
                                                    self.ssh_pass,
                                                    10)
        else:
            # Return a new client ssh object for the emulator node
            return util.netutil.ssh_connect_or_return2(self.ip,
                                                       int(self.ssh_port),
                                                       self.ssh_user,
                                                       self.ssh_pass,
                                                       10)

    def build(self):
        """ Wrapper to the SB-Emulator build handler
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
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
            self.status = 'NOT_BUILT'
            raise Exception('[SB-Emulator] Failure during building')

    def clean(self):
        """Wrapper to the SB-Emulator clean handler
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[SB-Emulator] Cleaning')
        self.status = 'CLEANING'

        exit_status = util.netutil.ssh_run_command(self._ssh_conn,
                                                   self.clean_hnd,
                                                   '[SB-Emulator.'
                                                   'clean_handler]')[0]
        if exit_status == 0:
            self.status = 'CLEANED'
            logging.info("[SB-Emulator] Successful clean")
        else:
            self.status = 'NOT_CLEANED'
            raise Exception('[SB-Emulator] Failure during cleaning')


class MTCBench(SBEmu):

    def __init__(self, sb_emu_base_dir, test_config):

        super(self.__class__, self).__init__(sb_emu_base_dir, test_config)

        self.run_hnd = self.base_dir + test_config['mtcbench_run_handler']

        '''check handlers' validity'''
        util.file_ops.check_filelist([self.run_hnd])

        # The parameters initialized as None are dimensions of the test.
        # These values are passed outside, from the test in the main for loop.
        # ---------------------------------------------------------------------
        self.simulated_hosts = None
        self.switches_per_thread = None
        self.threads = None
        self.thread_creation_delay_ms = None
        self.delay_before_traffic_ms = None
        # ---------------------------------------------------------------------
        self.mode = test_config['mtcbench_mode']
        self.warmup = test_config['mtcbench_warmup']
        self.ms_per_test = test_config['mtcbench_ms_per_test']
        self.internal_repeats = test_config['mtcbench_internal_repeats']

        self.rebuild = test_config['mtcbench_rebuild']

    def get_topo_bootup_ms(self):
        topo_bootup_ms = self.threads * self.thread_creation_delay_ms
        return topo_bootup_ms

    def get_overall_topo_size(self):
        overall_topo_size = self.threads * self.switches_per_thread
        return overall_topo_size

    def run(self, ctrl_ip, ctrl_sb_port):
        """ Wrapper to the MTCBench SB-Emulator run handler
        :param ctrl_ip: The ip address of the controller
        :param ctrl_sb_port: the port number of the SouthBound interface of
        the controller
        :type ctrl_ip: str
        :type ctrl_sb_port: int
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[MTCBench] Starting')
        self.status = 'STARTING'
        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([self.run_hnd,
                                                   ctrl_ip,
                                                   str(ctrl_sb_port),
                                                   str(self.threads),
                                                   str(self.switches_per_thread),
                                                   str(self.threads * self.switches_per_thread),
                                                   str(self.thread_creation_delay_ms),
                                                   str(self.delay_before_traffic_ms),
                                                   str(self.ms_per_test),
                                                   str(self.internal_repeats),
                                                   str(self.simulated_hosts),
                                                   str(self.warmup),
                                                   self.mode]),
                                         '[MTCBench.run_handler]')[0]
        if exit_status == 0:
            self.status = 'STARTED'
            logging.info("[MTCBench] Successful started")
        else:
            self.status = 'NOT_STARTED'
            raise Exception('[MTCBench] Failure during starting')


class Multinet(SBEmu):

    def __init__(self, sb_emu_base_dir, test_config):

        super(self.__class__, self).__init__(sb_emu_base_dir, test_config)
        print("BASE DIRECTORY:", self.base_dir)
        self.deploy_hnd = (self.base_dir +
                           test_config['topology_rest_server_boot'])
        self.cleanup_hnd = (self.base_dir +
                            test_config['topology_rest_server_stop'])
        self.master_rest_port = test_config['topology_rest_server_port']

        self.get_switches_hnd = (sb_emu_base_dir +
                                 test_config['topology_get_switches_handler'])

        if 'topology_traffic_gen_handler' in test_config:
            self.traffic_gen_hnd = \
                self.base_dir + test_config['topology_traffic_gen_handler']

        if 'topology_get_flows_handler' in test_config:
            self.get_flows_hnd = (self.base_dir +
                                  test_config['topology_get_flows_handler'])

        # The parameters initialized as None are dimensions of the test.
        # These values are passed outside, from the test in the main for loop.
        # ---------------------------------------------------------------------
        self.topo_size = None
        self.topo_type = None
        self.topo_hosts_per_switch = None
        self.topo_group_size = None
        self.topo_group_delay_ms = None
        # ---------------------------------------------------------------------

        self.init_topos_hnd = (self.base_dir +
                               test_config['topology_init_handler'])
        self.start_topos_hnd = (self.base_dir +
                                test_config['topology_start_switches_handler'])
        self.stop_topos_hnd = (self.base_dir +
                               test_config['topology_stop_switches_handler'])

        if 'multinet_traffic_gen_duration_ms' in test_config:
            self.traffic_gen_duration_ms = \
                test_config['multinet_traffic_gen_duration_ms']
        else:
            self.traffic_gen_duration_ms = 0
        if 'interpacket_delay_ms' in test_config:
            self.interpacket_delay_ms = test_config['interpacket_delay_ms']
        else:
            self.interpacket_delay_ms = 0

        self.topo_switch_type = test_config['multinet_switch_type']
        self.workers_ips = test_config['multinet_worker_ip_list']
        self.workers_ports = test_config['multinet_worker_port_list']

        self.__multinet_config_file_remote_path = os.path.join(self.base_dir,
                                                               "config",
                                                               "config.json")
        self.venv_hnd = self.base_dir + "bin/venv_handler_master.sh"

    def get_topo_bootup_ms(self):
        topo_bootup_ms = \
            (self.topo_size // self.topo_group_size) * self.topo_group_delay_ms
        return topo_bootup_ms

    def get_overall_topo_size(self):
        overall_topo_size = self.topo_size * len(self.workers_ips)
        return overall_topo_size

    def __generate_config(self, cntrl_of_port, cntrl_ip):
        """
        Generates a new json configuration file for multinet, according to the
        configuration values that are passed as parameters.
        :param cntrl_of_port: this is the southbound port of the controller,
        where it listens for openflow protocol messages
        :param cntrl_ip: IP address of controller node
        :type cntrl_of_port: int
        :type cntrl_ip: str
        :raises IOError: if it fails to create the configuration JSON file
        """
        config_data = {}
        config_data['master_ip'] = self.ip
        config_data['master_port'] = self.master_rest_port
        config_data['worker_ip_list'] = self.workers_ips
        config_data['worker_port_list'] = self.workers_ports
        config_data['deploy'] = {}
        config_data['deploy']['multinet_base_dir'] = self.base_dir
        config_data['deploy']['ssh_port'] = self.ssh_port
        config_data['deploy']['username'] = self.ssh_user
        config_data['deploy']['password'] = self.ssh_pass
        config_data['topo'] = {}
        config_data['topo']['controller_ip_address'] = cntrl_ip
        config_data['topo']['controller_of_port'] = cntrl_of_port
        config_data['topo']['switch_type'] = self.topo_switch_type
        config_data['topo']['topo_type'] = self.topo_type
        config_data['topo']['topo_size'] = self.topo_size
        config_data['topo']['group_size'] = self.topo_group_size
        config_data['topo']['group_delay'] = self.topo_group_delay_ms
        config_data['topo']['hosts_per_switch'] = self.topo_hosts_per_switch
        config_data['topo']['traffic_generation_duration_ms'] = \
            self.traffic_gen_duration_ms
        config_data['topo']['interpacket_delay_ms'] = self.interpacket_delay_ms

        with open(self.__multinet_config_file_local_path,
                  'w') as config_json_file:
            json.dump(config_data, config_json_file)
            print('CONFIG FILE PREPARED')
        if not util.file_ops.file_exists(self.__multinet_config_file_local_path):
            raise Exception('[Multinet] Config local file '
                            'has not been created')

    def __parse_output(self, multinet_handler_name, multinet_output):
        """Gets the console output of a multinet handler and extracts the
        aggregated result from all workers, as a numeric value.
        (Helper function)
        :param multinet_handler_name: The name of multinet handler from which
        we get the results.
        :param multinet_output: The console output of multinet handler
        :returns: The aggregated result from all workers
        (aggregation function is sum)
        :rtype: int
        :type multinet_handler_name: string
        :type multinet_output: string
        :raises exception: If the result of the parsed multinet output is None
        """
        regex_result = re.search(r'INFO:root:\[{0}\]\[response data\].*'.
                                 format(multinet_handler_name),
                                 multinet_output)
        if regex_result is None:
            raise Exception('Failed to get results from {0} multinet handler.'.
                            format(multinet_handler_name))
        else:
            json_result = \
                regex_result.group(0).replace('INFO:root:[{0}]'
                                              '[response data] '
                                              .format(multinet_handler_name),
                                              '')
        multinet_result = \
            sum([list(json.loads(v).values())[0] for v in json.loads(json_result)])
        return multinet_result

    def deploy(self, cntrl_ip, cntrl_of_port):
        """ Wrapper to the Multinet SB-Emulator deploy handler
        """
        logging.info('[Multinet] Deploy')
        self.status = 'DEPLOYING'
        self.__generate_config(cntrl_of_port, cntrl_ip)

        util.netutil.ssh_copy_file_to_target(self.ip,
                                             int(self.ssh_port),
                                             self.ssh_user,
                                             self.ssh_pass,
                                             self.__multinet_config_file_local_path,
                                             self.__multinet_config_file_remote_path)

        if not util.netutil.isfile(self.ip, self.ssh_port, self.ssh_user,
                                   self.ssh_pass, [self.deploy_hnd]):
            raise Exception('[Multinet] Deploy handler does not exist')

        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([self.venv_hnd,
                                                   self.base_dir,
                                                   self.deploy_hnd,
                                                   self.__multinet_config_file_remote_path]),
                                         '[Multinet.deploy_handler]')[0]
        if exit_status == 0:
            self.status = 'DEPLOYED'
            logging.info("[Multinet] Successful deployed")
        else:
            self.status = 'NOT_DEPLOYED'
            raise Exception('[Multinet] Failure during deploying')

    def get_switches(self, new_ssh_conn=None):
        """ Wrapper to the Multinet SB-Emulator get_switches handler
        :param new_ssh_conn: an SSH client connection object
        :returns: The per worker number of switches in json string
        :rtype: str
        :type new_ssh_conn: paramiko.SFTPClient
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[Multinet] get_switches')
        self.status = 'GETTING_SWITCHES'

        if not util.netutil.isfile(self.ip, self.ssh_port, self.ssh_user,
                                   self.ssh_pass, [self.get_switches_hnd]):
            raise Exception('[Multinet] Get_switches handler does not exist')
        if new_ssh_conn is not None:
            used_ssh_conn = new_ssh_conn
        else:
            used_ssh_conn = self._ssh_conn
        exit_status, output = \
            util.netutil.ssh_run_command(used_ssh_conn,
                                         ' '.join([self.venv_hnd,
                                                   self.base_dir,
                                                   self.get_switches_hnd,
                                                   self.__multinet_config_file_remote_path]),
                                         '[Multinet.get_switches_hnd]')
        if new_ssh_conn is not None:
            used_ssh_conn.close()
        if exit_status == 0:
            self.status = 'GOT_SWITCHES'
            logging.info("[Multinet] Successful got switches")
            return self.__parse_output('get_switches_topology_handler', output)
        else:
            self.status = 'NOT_GOT_SWITCHES'
            raise Exception('[Multinet] Failure during getting switches')

    def get_flows(self, new_ssh_conn=None):
        """ Wrapper to the Multinet SB-Emulator get_flows handler
        :param new_ssh_conn: an SSH client connection object
        :returns: The per worker total number of flows in json string
        :rtype: str
        :type new_ssh_conn: paramiko.SFTPClient
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[Multinet] get_flows')
        self.status = 'GETTING_FLOWS'

        if not util.netutil.isfile(self.ip, self.ssh_port, self.ssh_user,
                                   self.ssh_pass, [self.get_flows_hnd]):
            raise Exception('[Multinet] Get_flows handler does not exist')
        if new_ssh_conn is not None:
            used_ssh_conn = new_ssh_conn
        else:
            used_ssh_conn = self._ssh_conn
        exit_status, output = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([self.venv_hnd,
                                                   self.base_dir,
                                                   self.get_flows_hnd,
                                                   self.__multinet_config_file_remote_path]),
                                         '[Multinet. get_flows_hnd]')
        if new_ssh_conn is not None:
            used_ssh_conn.close()
        if exit_status == 0:
            self.status = 'GOT_FLOWS'
            logging.info("[Multinet] Successful got flows")
            return self.__parse_output('get_flows_topology_handler', output)
        else:
            self.status = 'NOT_GOT_FLOWS'
            raise Exception('[Multinet] Failure during getting flows')

    def init_topos(self):
        """ Wrapper to the Multinet SB-Emulator init_topos handler
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[Multinet] init_topos')
        self.status = 'INIT_MININET_TOPOS'

        if not util.netutil.isfile(self.ip, self.ssh_port, self.ssh_user,
                                   self.ssh_pass, [self.init_topos_hnd]):
            raise Exception('[Multinet] Init_topos handler does not exist')

        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([self.venv_hnd,
                                                   self.base_dir,
                                                   self.init_topos_hnd,
                                                   self.__multinet_config_file_remote_path]),
                                         '[Multinet.init_topos_hnd]')[0]

        if exit_status == 0:
            self.status = 'TOPOS_INITIALIZED'
            logging.info('[Multinet] Successful initialization '
                         'of Mininet topos')
        else:
            self.status = 'TOPOS_NOT_INITIALIZED'
            raise Exception('[Multinet] Failure during topos initialization')

    def start_topos(self):
        """ Wrapper to the Multinet SB-Emulator start_topos handler
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[Multinet] start_topos')
        self.status = 'START_MININET_TOPOS'

        if not util.netutil.isfile(self.ip, self.ssh_port, self.ssh_user,
                                   self.ssh_pass, [self.start_topos_hnd]):
            raise Exception('[Multinet] Start_topos handler does not exist')

        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([self.venv_hnd,
                                                   self.base_dir,
                                                   self.start_topos_hnd,
                                                   self.__multinet_config_file_remote_path]),
                                         '[Multinet.start_topos_hnd]')[0]
        if exit_status == 0:
            self.status = 'TOPOS_STARTED'
            logging.info('[Multinet] Successful start of Mininet topos')
        else:
            self.status = 'TOPOS_NOT_STARTED'
            raise Exception('[Multinet] Failure during the starting of topos')

    def stop_topos(self):
        """ Wrapper to the Multinet SB-Emulator stop_topos handler
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[Multinet] stop_topos')
        self.status = 'STOP_MININET_TOPOS'

        if not util.netutil.isfile(self.ip, self.ssh_port, self.ssh_user,
                                   self.ssh_pass, [self.stop_topos_hnd]):
            raise Exception('[Multinet] Stop_topos handler does not exist')

        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([self.venv_hnd,
                                                   self.base_dir,
                                                   self.stop_topos_hnd,
                                                   self.__multinet_config_file_remote_path]),
                                         '[Multinet.stop_topos_hnd]')[0]
        if exit_status == 0:
            self.status = 'TOPOS_STOPPED'
            logging.info('[Multinet] Successful stop of Mininet topos')
        else:
            self.status = 'TOPOS_NOT_STOPPED'
            raise Exception('[Multinet] Failure during the stopping of topos')

    def cleanup(self):
        """ Wrapper to the Multinet SB-Emulator cleanup handler
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[Multinet] cleanup')
        self.status = 'CLEANUP_MININET'

        if not util.netutil.isfile(self.ip, self.ssh_port, self.ssh_user,
                                   self.ssh_pass, [self.cleanup_hnd]):
            raise Exception('[Multinet] Cleanup handler does not exist')

        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([self.venv_hnd,
                                                   self.base_dir,
                                                   self.cleanup_hnd,
                                                   self.__multinet_config_file_remote_path]),
                                         '[Multinet.cleanup_hnd]')[0]
        if exit_status == 0:
            self.status = 'TOPOS_CLEANED'
            logging.info('[Multinet] Successful cleanup of Mininet topos')
        else:
            self.status = 'TOPOS_NOT_CLEANED'
            raise Exception('[Multinet] Failure during the cleanup of topos')

    def generate_traffic(self):
        """ Wrapper to the Multinet SB-Emulator traffic_gen handler
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[Multinet] traffic gen')
        self.status = 'CREATE_TRAFFIC'

        if not util.netutil.isfile(self.ip, self.ssh_port, self.ssh_user,
                                   self.ssh_pass, [self.traffic_gen_hnd]):
            raise Exception('[Multinet] Traffic_generator handler '
                            'does not exist')
        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([self.venv_hnd,
                                                   self.base_dir,
                                                   self.traffic_gen_hnd,
                                                   self.__multinet_config_file_remote_path]),
                                         '[Multinet.generate_traffic_hnd]')[0]
        if exit_status == 0:
            self.status = 'TRAFFIC_UP'
            logging.info('[Multinet] Successful traffic generation '
                         'from switches')
        else:
            self.status = 'TRAFFIC_DOWN'
            raise Exception('[Multinet] Failure during traffic generation '
                            'from switches')
