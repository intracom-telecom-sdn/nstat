# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NB-Generator Class- All NB-Generator-related functionality is here"""

# import emulators.nb_generator
import gevent
import logging
import os
import stress_test.nb_generator_exceptions
import sys
import time
import traceback
import util.netutil


class NBgen:
    """
    All NB-generator related functionality is here
    """

    def __init__(self, nb_gen_base_dir, test_config, controller, sbemu,
                 log_level="DEBUG"):
        """Create an NB-generator object. Options from JSON input file

        :param nb_gen_base_dir: emulator base directory
        :param test_config: JSON input configuration
        :param controller: object of the Controller class
        :param sbemu: object of the SBEmu subclass
        :param log_level: defines the logging level. (DEBUG, INFO, ERROR)
        :type nb_gen_base_dir: str
        :type test_config: JSON configuration dictionary
        :type controller: object
        :type sbemu: object
        :type log_level: str
        """
        self.controller = controller
        self.sbemu = sbemu
        self.name = test_config['nb_emulator_name']
        self.base_dir = nb_gen_base_dir
        self.traceback_enabled = True

        self.ip = test_config['nb_emulator_node_ip']
        self.ssh_port = test_config['nb_emulator_node_ssh_port']
        self.ssh_user = test_config['nb_emulator_node_username']
        self.ssh_pass = test_config['nb_emulator_node_password']
        self.build_hnd = (self.base_dir +
                          test_config['nb_emulator_build_handler'])
        self.clean_hnd = (self.base_dir +
                          test_config['nb_emulator_clean_handler'])
        self.run_hnd = (self.base_dir +
                        test_config['nb_emulator_run_handler'])
        self.run_hnd_path = os.path.dirname(self.run_hnd) + '/'

        self.get_oper_ds_flows_hnd = (
            self.base_dir + test_config['nb_emulator_get_oper_ds_handler'])

        self.status = 'UNKNOWN'
        self._ssh_conn = None

        self.flow_delete_flag = test_config['flow_delete_flag']
        self.flows_per_request = test_config['flows_per_request']
        self.log_level = log_level
        # The parameters initialized as None are dimensions of the test.
        # These values are passed outside, from the test in the main for loop.
        # ---------------------------------------------------------------------
        self.flow_workers = None
        self.total_flows = None
        self.flow_operations_delay_ms = None
        # ---------------------------------------------------------------------
        self.flows_ds_discovery_deadline = 240

        self.confirm_time = 0.0
        self.e2e_installation_time = 0.0
        self.discover_flows_on_switches_time = 0.0

        self.venv_hnd = self.base_dir + "bin/venv_handler.sh"
        print('=====================================')
        print('=====================================')
        print('=====================================')
        print(nb_gen_base_dir)
        print('=====================================')
        print('=====================================')
        print('=====================================')

    def _error_handling(self, error_message, error_num=1):
        """
        Handles custom errors of nb_generator

        :param error_message: message of the handled error
        :param error_num: error number of the handled error, used to define
        subcases of raised errors.
        :type error_message: str
        :type error_num: int
        :raises nb_generator_exceptions.NBGenError: to terminate execution of
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
        raise(stress_test.nb_generator_exceptions.NBGenError)

    def init_ssh(self):
        """
        Initializes a new SSH client object, with the nb_generator node and \
            assigns it to the protected attribute _ssh_conn. If a connection \
            already exists it returns a new SSH client object to the  \
            controller node.

        :raises nb_generator_exceptions.NBGenNodeConnectionError: if ssh \
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
                    # Return a new client ssh object for the nb-generator node
                    return util.netutil.ssh_connect_or_return(
                        self.ip, int(self.ssh_port), self.ssh_user,
                        self.ssh_pass, 10)
            except:
                raise(stress_test.nb_generator_exceptions.NBGenNodeConnectionError)
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self._error_handling(e.err_msg, e.err_code)

    def build(self):
        """
        Wrapper to the NB-Generator build handler

        :raises IOError: if the handler does not exist on the remote host
        :raises nb_generator_exceptions.NBGenBuildError: if build process fails
        """
        logging.info('[NB_generator] Building')
        self.status = 'BUILDING'
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.build_hnd]):
                    self.status = 'NOT_BUILT'
                    raise(IOError(
                        '{0} build handler does not exist'.
                        format('[nb_generator.build]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.build_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join([self.build_hnd]),
                    '[NB_generator.build_handler]')
                if exit_status == 0:
                    self.status = 'BUILT'
                    logging.info("[NB_generator] Successful building")
                else:
                    self.status = 'NOT_BUILT'
                    raise(stress_test.nb_generator_exceptions.NBGenBuildError(
                        '[NB_generator] Failure during running. Build handler '
                        'exited with no zero exit status. \n '
                        'Handler output: {0}'.format(cmd_output), exit_status))
            except stress_test.nb_generator_exceptions.NBGenError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.nb_generator_exceptions.NBGenBuildError(
                    '[NB_generator] Build handler was not executed at all. '
                    'Failure running the handler.'))
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self._error_handling(e.err_msg, e.err_code)

    def clean(self):
        """
        Wrapper to the NB-Generator clean handler

        :raises IOError: if the handler does not exist on the remote host
        :raises nb_generator_exceptions.NBGenCleanError: if clean process fails
        """
        logging.info('[NB_generator] Cleaning')
        self.status = 'CLEANING'
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.clean_hnd]):
                    self.status = 'NOT_CLEANED'
                    raise(IOError(
                        '{0} clean handler does not exist'.
                        format('[nb_generator.clean]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.clean_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, self.clean_hnd,
                    '[NB_generator.clean_handler]')
                if exit_status == 0:
                    self.status = 'CLEANED'
                    logging.info("[NB_generator] Successful clean")
                else:
                    self.status = 'NOT_CLEANED'
                    raise(stress_test.nb_generator_exceptions.NBGenCleanError(
                        '[NB_generator] Failure during running. Clean handler '
                        'exited with no zero exit status. \n '
                        'Handler output: {0}'.format(cmd_output), exit_status))
            except stress_test.nb_generator_exceptions.NBGenError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.nb_generator_exceptions.NBGenCleanError(
                    '[NB_generator] Clean handler was not executed at all. '
                    'Failure running the handler.'))
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self._error_handling(e.err_msg, e.err_code)

    def run(self):
        """
        Wrapper to the NB-Generator run handler

        :returns: Returns the combined stdout - stderr of the executed command
        :rtype: str
        :raises IOError: if the handler does not exist on the remote host
        :raises nb_generator_exceptions.NBGenRunError: if running \
            nb_generator fails
        """
        logging.info("[NB_generator] Run handler")
        self.status = 'STARTED'
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.run_hnd]):
                    self.status = 'NB_GEN_NOT_RUNNING'
                    raise(IOError(
                        '{0} run handler does not exist'.
                        format('[nb_generator.run]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.run_hnd)
                exit_status, cmd_output = \
                    util.netutil.ssh_run_command(
                        self._ssh_conn,
                        ' '.join([str(self.venv_hnd),
                                  str(self.run_hnd_path),
                                  str(self.run_hnd),
                                  str(self.controller.ip),
                                  str(self.controller.restconf_port),
                                  str(self.total_flows),
                                  str(self.flow_workers),
                                  str(self.flow_operations_delay_ms),
                                  str(self.flow_delete_flag),
                                  str(self.controller.restconf_user),
                                  str(self.controller.restconf_pass),
                                  str(self.flows_per_request),
                                  str(self.log_level)]),
                        '[NB_generator] run_handler')
                if exit_status == 0:
                    self.status = 'NB_GEN_RUNNING'
                    logging.info("[NB_generator] up and running")
                else:
                    self.status = 'NB_GEN_NOT_RUNNING'
                    raise(stress_test.nb_generator_exceptions.NBGenRunError(
                        '[NB_generator] Failure during running. {0}'.
                        format(cmd_output), exit_status))
                return cmd_output
            except stress_test.nb_generator_exceptions.NBGenError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.nb_generator_exceptions.NBGenRunError)
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self._error_handling(e.err_msg, e.err_code)

    def __del__(self):
        """
        Method called when object is destroyed"""
        try:
            logging.info('Closing NB-Generator ssh connection.')
            self._ssh_conn.close()
        except:
            pass
