# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
SB-Emulator Class- All SB-Emulator-related functionality is here"""


import json
import logging
import os
import re
import stress_test.sbemu_exceptions
import sys
import traceback
import util.netutil
import util.file_ops


class SBEmu:
    """
    Southbound emulator super class
    """
    def __init__(self, sb_emu_base_dir, test_config):
        """
        Creates an SB-Emulator object. Options from JSON input file

        :param test_config: JSON input configuration
        :param sb_emu_base_dir: emulator base directory
        :type test_config: JSON configuration dictionary
        :type sb_emu_base_dir: str
        """
        self.name = test_config['sb_emulator_name']
        self.base_dir = sb_emu_base_dir
        self.traceback_enabled = False
        self.ip = test_config['sb_emulator_node_ip']
        self.ssh_port = test_config['sb_emulator_node_ssh_port']
        self.ssh_user = test_config['sb_emulator_node_username']
        self.ssh_pass = test_config['sb_emulator_node_password']

        self.build_hnd = (self.base_dir +
                          test_config['sb_emulator_build_handler'])
        self.clean_hnd = (self.base_dir +
                          test_config['sb_emulator_clean_handler'])
        self._ssh_conn = None
        util.file_ops.check_filelist([self.build_hnd,
                                      self.clean_hnd])

    @staticmethod
    def new(sb_emu_base_dir, test_config):
        """
        Factory method. Creates a subclass class depending on the \
            SB-Emulator name

        :param test_config: JSON input configuration
        :param sb_emu_base_dir: emulator base directory
        :returns: a subclass or None
        :type test_config: JSON configuration dictionary
        :type sb_emu_base_dir: str
        :rtype: object
        :raises NotImplementedError: in case an invalid sb_emulator_name is \
            given in the json configuration file
        """
        name = test_config['sb_emulator_name']
        if (name == 'MTCBENCH'):
            return MTCBench(sb_emu_base_dir, test_config)
        elif (name == 'MULTINET'):
            return Multinet(sb_emu_base_dir, test_config)
        else:
            raise NotImplementedError('Not supported yet')

    def _error_handling(self, error_message, error_num=1):
        """
        Handles custom errors of sb emulators

        :param error_message: message of the handled error
        :param error_num: error number of the handled error, used to define
        subcases of raised errors.
        :type error_message: str
        :type error_num: int
        :raises controller_exceptions.SBEmuError: to terminate execution of
        test after error handling
        """
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error('{0} :::::::::: Exception :::::::::::'.
                      format(exc_obj))
        logging.error(error_message)
        logging.error('Error number: {0}'.format(error_num))
        logging.error('{0} - {1} Exception: {2}, {3}'.
                      format(exc_obj, self.name, exc_type, exc_tb.tb_lineno))
        if self.traceback_enabled:
            traceback.print_exc()
        raise(stress_test.sbemu_exceptions.SBEmuError)

    def init_ssh(self):
        """
        Initializes a new SSH client object, with the emulator node and \
            assigns it to the protected attribute _ssh_conn. If a connection \
            already exists it returns a new SSH client object to the  \
            controller node.

        :raises emulator_exceptions.SBEmuNodeConnectionError: if ssh \
            connection establishment fails
        """
        logging.info(
            '[open_ssh_connection] Initiating SSH session with {0} node on '
            '{1} host.'.format(self.name, self.ip))
        try:
            try:
                if self._ssh_conn is None:
                    self._ssh_conn = util.netutil.ssh_connect_or_return(
                        self.ip, int(self.ssh_port), self.ssh_user,
                        self.ssh_pass, 10)
                else:
                    # Return a new client ssh object for the emulator node
                    return util.netutil.ssh_connect_or_return(
                        self.ip, int(self.ssh_port), self.ssh_user,
                        self.ssh_pass, 10)
            except:
                raise(stress_test.sbemu_exceptions.SBEmuNodeConnectionError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def build(self):
        """
        Wrapper to the SB-Emulator build handler

        :raises IOError: if the handler does not exist on the remote host
        :raises emulator_exceptions.SBEmuBuildError: build fails
        """
        logging.info('[SB-Emulator] Building')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.build_hnd]):
                    raise(IOError(
                        '{0} build handler does not exist'.
                        format('[SB-Emulator.build_handler]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.build_hnd)
                    exit_status, cmd_output = util.netutil.ssh_run_command(
                        self._ssh_conn, ' '.join([self.build_hnd]),
                        '[SB-Emulator.build_handler]')
                    if exit_status == 0:
                        logging.info("[SB-Emulator] Successful building")
                    else:
                        raise(stress_test.sbemu_exceptions.SBEmuBuildError(
                            '[SB-Emulator] Failure during building: {0}'.
                            format(cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.SBEmuBuildError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def clean(self):
        """
        Wrapper to the SB-Emulator clean handler

        :raises IOError: if the handler does not exist on the remote host
        :raises emulator_exceptions.SBEmuCleanupError: if cleanup process fails
        """
        logging.info('[SB-Emulator] Cleaning')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.clean_hnd]):
                    raise(IOError(
                        '{0} clean handler does not exist'.
                        format('[SB-Emulator.clean_handler]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.clean_hnd)
                    exit_status, cmd_output = util.netutil.ssh_run_command(
                        self._ssh_conn, self.clean_hnd,
                        '[SB-Emulator.clean_handler]')
                    if exit_status == 0:
                        logging.info("[SB-Emulator] Successful clean")
                    else:
                        raise(stress_test.sbemu_exceptions.
                              SBEmuCleanupError(
                                  '[SB-Emulator] Failure during cleaning: {0}'.
                                  format(cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.SBEmuCleanupError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def __del__(self):
        """
        Method called when object is destroyed
        """
        try:
            logging.info('Run SB-Emulator clean handler.')
            self.clean()
        except Exception as e:
            logging.info('Fail cleaning SB-Emulator during '
                         'cleanup. Exception message: {0}'.format(e))
        try:
            logging.info('Close emulator node ssh connection.')
            self._ssh_conn.close()
        except Exception as e:
            logging.info('Fail closing ssh SB-Emulator node connection during '
                         'cleanup. Exception message: {0}'.format(e))


class MTCBench(SBEmu):
    """
    All South-bound MTCbench related functionality is here
    """
    def __init__(self, sb_emu_base_dir, test_config):
        """
        Initialize the creation of an MTCbench SB emulator object.
        Inherits from SBEmu class.

        :param sb_emu_base_dir: emulator base directory
        :param test_config: JSON input configuration
        :type sb_emu_base_dir: str
        :type test_config: JSON configuration dictionary
        """
        super(self.__class__, self).__init__(sb_emu_base_dir, test_config)

        self.run_hnd = self.base_dir + test_config['mtcbench_run_handler']

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

    def get_topo_bootup_ms(self):
        """
        Calculates and returns the total topology bootup time in ms.

        :returns: the total time for the topology to bootup
        :rtype: int
        """
        topo_bootup_ms = self.threads * self.thread_creation_delay_ms
        return topo_bootup_ms

    def get_overall_topo_size(self):
        """
        Calculates and returns the total topology size.

        :returns: the total switch number
        :rtype: int
        """
        overall_topo_size = self.threads * self.switches_per_thread
        return overall_topo_size

    def run(self, ctrl_ip, ctrl_sb_port, prefix='[MTCBench.run_handler]',
            lines_queue=None, print_flag=True, block_flag=True,
            getpty_flag=False):
        """
        Wrapper to the MTCBench SB-Emulator run handler

        :param ctrl_ip: The ip address of the controller
        :param ctrl_sb_port: the port number of the SouthBound interface of \
            the controller
        :param prefix: prefix of logging messages printed during execution of \
            MTCbench handler
        :param lines_queue: a queue object gathering the output of MTCbench \
            handler line by line.
        :param print_flag: defines if the output of MTCbench handler will be \
            printed on the screen
        :param block_flag: defines if the run handler will run in blocking or \
            non blocking mode. In not blocking mode no output will be printed \
            or saved in a queue.
        :param getpty_flag: defines if the run handler will run in a separate \
            pty terminal
        :type ctrl_ip: str
        :type ctrl_sb_port: int
        :type prefix: str
        :type lines_queue: gevent.queue.Queue()
        :type print_flag: bool
        :type block_flag: bool
        :type getpty_flag: bool
        :raises IOError: if the exit status of the handler is not 0
        :raises emulator_exceptions.MTCbenchRunError: in case of run MTCbench \
            error
        """
        logging.info('{0} Starting'.format(prefix))
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.run_hnd]):
                    raise(IOError(
                        '{0} run handler does not exist'.format(prefix)))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.run_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join(
                        [self.run_hnd, ctrl_ip, str(ctrl_sb_port),
                         str(self.threads), str(self.switches_per_thread),
                         str(self.threads * self.switches_per_thread),
                         str(self.thread_creation_delay_ms),
                         str(self.delay_before_traffic_ms),
                         str(self.ms_per_test), str(self.internal_repeats),
                         str(self.simulated_hosts), str(self.warmup),
                         self.mode]),
                    prefix, lines_queue, print_flag,
                    block_flag, getpty_flag)
                if exit_status == 0:
                    logging.info('{0} Successful started'.format(prefix))
                else:
                    raise(stress_test.sbemu_exceptions.MTCbenchRunError(
                        '{0} Failure during starting: {1}'.
                        format(prefix, cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.MTCbenchRunError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)


class Multinet(SBEmu):
    """
    All South-bound Multinet related functionality is here
    """
    def __init__(self, sb_emu_base_dir, test_config):
        """
        Initialize the creation of an Multinet SB emulator object.
        Inherits from SBEmu class.

        :param sb_emu_base_dir: emulator base directory
        :param test_config: JSON input configuration
        :type sb_emu_base_dir: str
        :type test_config: JSON configuration dictionary
        """
        super(self.__class__, self).__init__(sb_emu_base_dir, test_config)
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
        if 'multinet_interpacket_delay_ms' in test_config:
            self.interpacket_delay_ms = \
                test_config['multinet_interpacket_delay_ms']
        else:
            self.interpacket_delay_ms = 0

        self.topo_switch_type = test_config['multinet_switch_type']
        self.workers_ips = test_config['multinet_worker_ip_list']
        self.workers_ports = test_config['multinet_worker_port_list']
        self.__multinet_config_file_local_path = os.path.join(self.base_dir,
                                                              "config.json")
        self.__multinet_config_file_remote_path = os.path.join(self.base_dir,
                                                               "config",
                                                               "config.json")
        self.venv_hnd = self.base_dir + "bin/venv_handler_master.sh"

    def get_topo_bootup_ms(self):
        """
        Calculates and returns the total topology bootup time in ms.

        :returns: the total time for the topology to bootup
        :rtype: int
        """
        topo_bootup_ms = \
            (self.topo_size // self.topo_group_size) * self.topo_group_delay_ms
        return topo_bootup_ms

    def get_overall_topo_size(self):
        """
        Calculates and returns the total topology size.

        :returns: the total worker number
        :rtype: int
        """
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
        :raises emulator_exceptions.MultinetConfGenerateError: if json
        configuration file generation of multinet fails
        """
        try:
            try:
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
                config_data['topo']['hosts_per_switch'] = \
                    self.topo_hosts_per_switch
                config_data['topo']['traffic_generation_duration_ms'] = \
                    self.traffic_gen_duration_ms
                config_data['topo']['interpacket_delay_ms'] = \
                    self.interpacket_delay_ms

                with open(self.__multinet_config_file_local_path,
                          'w') as config_json_file:
                    json.dump(config_data, config_json_file)
                if not util.file_ops.file_exists(self.__multinet_config_file_local_path):
                    raise(stress_test.sbemu_exceptions.MultinetConfGenerateError(
                        '[Multinet] Config local file has not been created',
                        2))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(
                    stress_test.sbemu_exceptions.MultinetConfGenerateError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def __parse_output(self, multinet_handler_name, multinet_output):
        """
        Gets the console output of a multinet handler and extracts the
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
        :raises emulator_exceptions.MultinetOutputParsingError: If the result
        of the parsed multinet output is None
        """
        try:
            try:
                regex_result = re.search(
                    r'INFO:root:\[{0}\]\[response data\].*'.
                    format(multinet_handler_name), multinet_output)
                if regex_result is None:
                    raise(stress_test.sbemu_exceptions.MultinetOutputParsingError(
                        'Failed to get results from {0} multinet handler.'.
                        format(multinet_handler_name), 2))
                else:
                    json_result = regex_result.group(0).replace(
                        'INFO:root:[{0}][response data] '
                        .format(multinet_handler_name), '')
                multinet_result = \
                    sum([list(json.loads(v).values())[0] for v in json.loads(json_result)])
                return multinet_result
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(
                    stress_test.sbemu_exceptions.MultinetOutputParsingError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def deploy(self, cntrl_ip, cntrl_of_port):
        """
        Wrapper to the Multinet SB-Emulator deploy handler

        :param cntrl_ip: The IP of the Controller.
        :param cntrl_of_port: The openflow interface port of the Controller
        :type cntrl_ip: str
        :type cntrl_of_port: int
        :raises IOError: if the handler does not exist on the remote host
        :raises emulator_exceptions.MultinetDeployError: in case of Multinet \
            deploy error
        """
        logging.info('[Multinet] Deploy')
        try:
            try:
                self.__generate_config(cntrl_of_port, cntrl_ip)
                util.netutil.ssh_copy_file_to_target(
                    self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                    self.__multinet_config_file_local_path,
                    self.__multinet_config_file_remote_path)

                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.deploy_hnd]):
                    raise(IOError(
                        '[Multinet] Deploy handler does not exist'))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.deploy_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join(
                        [self.venv_hnd, self.base_dir, self.deploy_hnd,
                         self.__multinet_config_file_remote_path]),
                    '[Multinet.deploy_handler]')
                if exit_status == 0:
                    logging.info('[Multinet] Successful deployed')
                else:
                    raise(stress_test.sbemu_exceptions.MultinetDeployError(
                        '[Multinet] Failure during deploying: {0}'.
                        format(cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.MultinetDeployError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def get_switches(self, new_ssh_conn=None):
        """
        Wrapper to the Multinet SB-Emulator get_switches handler

        :param new_ssh_conn: an SSH client connection object
        :returns: The per worker number of switches in json string
        :rtype: strcleanup_hnd
        :type new_ssh_conn: paramiko.SFTPClient
        :raises IOError: if the handler does not exist on the remote host
        :raises emulator_exceptions.MultinetGetSwitchesError: if handler \
            fails to run successfully and return a valid result
        """
        logging.info('[Multinet] get_switches')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.get_switches_hnd]):
                    raise(IOError(
                        '[Multinet] Get_switches handler does not exist'))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.get_switches_hnd)
                if new_ssh_conn is not None:
                    used_ssh_conn = new_ssh_conn
                else:
                    used_ssh_conn = self._ssh_conn
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    used_ssh_conn, ' '.join(
                        [self.venv_hnd, self.base_dir, self.get_switches_hnd,
                         self.__multinet_config_file_remote_path]),
                    '[Multinet.get_switches_hnd]')
                if new_ssh_conn is not None:
                    used_ssh_conn.close()
                if exit_status == 0:
                    logging.info("[Multinet] Successful got switches")
                    return self.__parse_output('get_switches_topology_handler',
                                               cmd_output)
                else:
                    raise(stress_test.sbemu_exceptions.MultinetGetSwitchesError(
                        '[Multinet] Failure during getting switches: {0}'.
                        format(cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.MultinetGetSwitchesError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def get_flows(self, new_ssh_conn=None):
        """
        Wrapper to the Multinet SB-Emulator get_flows handler

        :param new_ssh_conn: an SSH client connection object
        :returns: The per worker total number of flows in json string
        :rtype: str
        :type new_ssh_conn: paramiko.SFTPClient
        :raises IOError: if the handler does not exist on the remote host
        :raises emulator_exceptions.MultinetGetFlowsError: if handler fails to
            run successfully
        """
        logging.info('[Multinet] get_flows')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.get_flows_hnd]):
                    raise(IOError(
                        '[Multinet] Get_flows handler does not exist'))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.get_flows_hnd)
                if new_ssh_conn is not None:
                    used_ssh_conn = new_ssh_conn
                else:
                    used_ssh_conn = self._ssh_conn
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join(
                        [self.venv_hnd, self.base_dir,
                         self.get_flows_hnd,
                         self.__multinet_config_file_remote_path]),
                    '[Multinet. get_flows_hnd]')
                if new_ssh_conn is not None:
                    used_ssh_conn.close()
                if exit_status == 0:
                    logging.info("[Multinet] Successful got flows")
                    return self.__parse_output('get_flows_topology_handler',
                                               cmd_output)
                else:
                    raise(stress_test.sbemu_exceptions.MultinetGetFlowsError(
                        '[Multinet] Failure during getting flows: {0}'.
                        format(cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.MultinetGetFlowsError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def init_topos(self):
        """
        Wrapper to the Multinet SB-Emulator init_topos handler

        :raises IOError: if the handler does not exist on the remote host
        :raises emulator_exceptions.MultinetInitToposError: if Multinet \
            initialization fails
        """
        logging.info('[Multinet] init_topos')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.init_topos_hnd]):
                    raise(IOError(
                        '[Multinet] Init_topos handler does not exist'))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.init_topos_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join(
                        [self.venv_hnd, self.base_dir, self.init_topos_hnd,
                         self.__multinet_config_file_remote_path]),
                    '[Multinet.init_topos_hnd]')
                if exit_status == 0:
                    logging.info('[Multinet] Successful initialization '
                                 'of Mininet topos')
                else:
                    raise(stress_test.sbemu_exceptions.MultinetInitToposError(
                        '[Multinet] Failure during topos initialization: {0}'.
                        format(cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.MultinetInitToposError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def start_topos(self):
        """
        Wrapper to the Multinet SB-Emulator start_topos handler

        :raises IOError: if the handler does not exist on the remote host
        :raises emulator_exceptions.MultinetStartToposError: if Multinet start
            topology handler fails
        """
        logging.info('[Multinet] start_topos')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.start_topos_hnd]):
                    raise(IOError(
                        '[Multinet] Start_topos handler does not exist'))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.start_topos_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join(
                        [self.venv_hnd, self.base_dir, self.start_topos_hnd,
                         self.__multinet_config_file_remote_path]),
                    '[Multinet.start_topos_hnd]')
                if exit_status == 0:
                    logging.info('[Multinet] Successful start '
                                 'of Mininet topos')
                else:
                    raise(stress_test.sbemu_exceptions.MultinetStartToposError(
                        '[Multinet] Failure during the starting of topos: {0}'.
                        format(cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.MultinetStartToposError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def stop_topos(self):
        """
        Wrapper to the Multinet SB-Emulator stop_topos handler

        :raises IOError: if the handler does not exist on the remote host
        :raises emulator_exceptions.MultinetStopToposError: if Multinet stop \
            handler fails
        """
        logging.info('[Multinet] stop_topos')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.stop_topos_hnd]):
                    raise(IOError(
                        '[Multinet] Stop_topos handler does not exist'))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.stop_topos_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join(
                        [self.venv_hnd, self.base_dir, self.stop_topos_hnd,
                         self.__multinet_config_file_remote_path]),
                    '[Multinet.stop_topos_hnd]')
                if exit_status == 0:
                    logging.info('[Multinet] Successful stop of Mininet topos')
                else:
                    raise(stress_test.sbemu_exceptions.MultinetStopToposError(
                        '[Multinet] Failure during the stopping of topos'.
                        format(cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.MultinetStopToposError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def cleanup(self):
        """
        Wrapper to the Multinet SB-Emulator cleanup handler

        :raises IOError: if the handler does not exist on the remote host
        :raises emulator_exceptions.MultinetCleanupError: if Multinet cleanup \
            handler fails
        """
        logging.info('[Multinet] cleanup')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.cleanup_hnd]):
                    raise(IOError(
                        '[Multinet] Cleanup handler does not exist'))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.cleanup_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join(
                        [self.venv_hnd, self.base_dir, self.cleanup_hnd,
                         self.__multinet_config_file_remote_path]),
                    '[Multinet.cleanup_hnd]')
                if exit_status == 0:
                    logging.info('[Multinet] Successful cleanup of Mininet '
                                 'topos')
                else:
                    raise(stress_test.sbemu_exceptions.MultinetCleanupError(
                        '[Multinet] Failure during the cleanup of topos: {0}'.
                        format(cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.MultinetCleanupError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def generate_traffic(self):
        """
        Wrapper to the Multinet SB-Emulator traffic_gen handler

        :raises IOError: if the handler does not exist on the remote host
        :raises emulator_exceptions.MultinetTraffigGenError: if Multinet \
            traffic generator handler fails to run successfully
        """
        logging.info('[Multinet] traffic gen')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.traffic_gen_hnd]):
                    raise(IOError('[Multinet] Traffic_generator handler '
                                  'does not exist'))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.traffic_gen_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join(
                        [self.venv_hnd, self.base_dir, self.traffic_gen_hnd,
                         self.__multinet_config_file_remote_path]),
                    '[Multinet.generate_traffic_hnd]')
                if exit_status == 0:
                    logging.info('[Multinet] Successful traffic generation '
                                 'from switches')
                else:
                    raise(stress_test.sbemu_exceptions.
                          MultinetTraffigGenError(
                              '[Multinet] Failure during traffic generation '
                              'from switches: {0}'.
                              format(cmd_output), exit_status))
            except stress_test.sbemu_exceptions.SBEmuError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.sbemu_exceptions.MultinetTraffigGenError)
        except stress_test.sbemu_exceptions.SBEmuError as e:
            self._error_handling(e.err_msg, e.err_code)

    def __del__(self):
        """
        Method called when object is destroyed
        """
        try:
            logging.info('Run Multinet cleanup.')
            self.cleanup()
        except Exception as e:
            logging.info('Fail cleaning Multinet during '
                         'cleanup. Exception message: {0}'.format(e))
        super(self.__class__, self).__del__()
