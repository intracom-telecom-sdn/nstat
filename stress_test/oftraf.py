# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Oftraf Class- All oftraf monitor-related functionality is here. Note that
Oftraf Monitor runs thereto the controller is located (Controller-SB
interface) """

import logging
import os
import requests
import stress_test.oftraf_exceptions
import sys
import traceback
import util.netutil


class Oftraf:

    def __init__(self, controller, test_config):
        """Create an Oftraf Monitor Controller object.
        Options from JSON input file
        :param controller: object of the Controller class
        :param test_config: JSON input configuration
        :type controller: object
        :type test_config: parsed json file with test configuration
        """
        if 'oftraf_test_interval_ms' in test_config:
            self.interval_ms = test_config['oftraf_test_interval_ms']
        else:
            self.interval_ms = 0
        self.rest_server_port = test_config['oftraf_rest_server_port']
        self.rest_server_ip = controller.ip
        self.of_port = controller.of_port
        self.status = 'UNKNOWN'
        self._ssh_conn = controller.init_ssh()
        self.traceback_enabled = False

    def error_handling(self, error_message, error_num=1):
        """Handles custom errors of oftraf
        :param error_message: message of the handled error
        :param error_num: error number of the handled error, used to define
        subcases of raised errors.
        :type error_message: str
        :type error_num: int
        :raises oftraf_exceptions.OftrafError: to terminate execution of
        test after error handling
        """
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error('{0} :::::::::: Exception :::::::::::'.
                      format(exc_obj))
        logging.error(error_message)
        logging.error('Error number:{0}'.format(error_num))
        logging.error('{0} - {1} Exception: {2}, {3}'.
                      format(exc_obj, self.name, exc_type, exc_tb.tb_lineno))
        if self.traceback_enabled:
            traceback.print_exc()
        # Propagate error outside the class to stop execution
        raise(stress_test.oftraf_exceptions.OftrafError)

    def get_oftraf_path(self):
        """Returns oftraf base directory path, using as base to the project
        path
        :returns: oftraf folder path
        :rtype: str
        """
        stress_test_base_dir = os.path.abspath(os.path.join(
            os.path.realpath(__file__), os.pardir))
        monitors_base_dir = os.path.abspath(os.path.join(stress_test_base_dir,
                                                         os.pardir))
        oftraf_path = os.path.sep.join(
            [monitors_base_dir, 'monitors', 'oftraf', ''])
        return str(oftraf_path)

    def build(self):
        """ Wrapper to the oftraf monitor build handler
        :raises oftraf_exceptions.OftrafBuildError: if build process fails
        """
        try:
            try:
                oftraf_path = str(self.get_oftraf_path())
                build_hnd = os.path.join(str(oftraf_path), 'build.sh')
                logging.info('[Oftraf] Building')
                self.status = 'BUILDING'
                exit_status, cmd_output = \
                    util.netutil.ssh_run_command(self._ssh_conn,
                                                 ' '.join([build_hnd]),
                                                 '[oftraf.build_handler]')
                if exit_status == 0:
                    self.status = 'BUILT'
                    logging.info("[Oftraf] Successful building")
                else:
                    self.status = 'NOT_BUILT'
                    raise(stress_test.oftraf_exceptions.OftrafBuildError(
                        'Build process exited with non zero exit code. '
                        'Command-line output: {0} \n Exit status code: {1}'.
                        format(cmd_output, exit_status), 2))
            except stress_test.oftraf_exceptions.OftrafError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.oftraf_exceptions.OftrafBuildError)
        except stress_test.oftraf_exceptions.OftrafError as e:
            self.error_handling(e.err_msg, e.err_code)

    def clean(self):
        """ Wrapper to the oftraf monitor clean handler
        :raises oftraf_exceptions.OftrafCleanError: if clean process fails
        """
        try:
            try:
                oftraf_path = self.get_oftraf_path()
                clean_hnd = oftraf_path + 'clean.sh'
                logging.info('[Oftraf] Cleaning')
                self.status = 'CLEANING'

                exit_status, cmd_output = \
                    util.netutil.ssh_run_command(self._ssh_conn,
                                                 ' '.join([clean_hnd]),
                                                 '[oftraf.clean_handler]')
                if exit_status == 0:
                    self.status = 'CLEANED'
                    logging.info("[Oftraf] Successful cleaning")
                else:
                    self.status = 'NOT CLEANED'
                    raise(stress_test.oftraf_exceptions.OftrafCleanError(
                        'clean process exited with non zero exit code. '
                        'Command-line output: {0} \n Exit status code: {1}'.
                        format(cmd_output, exit_status), 2))
            except stress_test.oftraf_exceptions.OftrafError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.oftraf_exceptions.OftrafCleanError)
        except stress_test.oftraf_exceptions.OftrafError as e:
            self.error_handling(e.err_msg, e.err_code)

    def start(self):
        """ Wrapper to the oftraf monitor start handler. Initializes the REST
        interface of oftraf and listen of traffic on controller Southbound
        interface
        :raises oftraf_exceptions.OftrafStartError: if start process fails
        """
        try:
            try:
                oftraf_path = self.get_oftraf_path()
                start_hnd = oftraf_path + 'start.sh'
                logging.info('[Oftraf] Starting')
                self.status = 'STARTING'
                exit_status, cmd_output = \
                    util.netutil.ssh_run_command(
                        self._ssh_conn, ' '.join([start_hnd,
                                                  self.rest_server_ip,
                                                  str(self.rest_server_port),
                                                  str(self.of_port)]),
                        '[oftraf.start_handler]',
                        lines_queue=None, print_flag=True, block_flag=True,
                        getpty_flag=True)
                if exit_status == 0:
                    self.status = 'STARTED'
                    logging.info("[Oftraf] Successful starting")
                else:
                    self.status = 'NOT STARTED'
                    raise(stress_test.oftraf_exceptions.OftrafStartError(
                        'Start process exited with non zero exit code. '
                        'Command-line output: {0} \n Exit status code: {1}'.
                        format(cmd_output, exit_status), 2))
            except stress_test.oftraf_exceptions.OftrafError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.oftraf_exceptions.OftrafStartError)
        except stress_test.oftraf_exceptions.OftrafError as e:
            self.error_handling(e.err_msg, e.err_code)

    def stop(self):
        """ Wrapper to the oftraf monitor stop handler
        :raises oftraf_exceptions.OftrafStopError: if stop process fails
        """
        try:
            try:
                oftraf_path = self.get_oftraf_path()
                stop_hnd = oftraf_path + 'stop.sh'
                logging.info('[Oftraf] Starting')
                self.status = 'STOPPING'
                exit_status, cmd_output = \
                    util.netutil.ssh_run_command(
                        self._ssh_conn,
                        ' '.join([stop_hnd,
                                  self.rest_server_ip,
                                  str(self.rest_server_port)]),
                        '[oftraf.stop_handler]')
                if exit_status == 0:
                    self.status = 'STOPED'
                    logging.info("[Oftraf] Successful stopping")
                else:
                    self.status = 'NOT STOPPED'
                    raise(stress_test.oftraf_exceptions.OftrafStopError(
                        'Stop process exited with non zero exit code. '
                        'Command-line output: {0} \n Exit status code: {1}'.
                        format(cmd_output, exit_status), 2))
            except stress_test.oftraf_exceptions.OftrafError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.oftraf_exceptions.OftrafStopError)
        except stress_test.oftraf_exceptions.OftrafError as e:
            self.error_handling(e.err_msg, e.err_code)

    def oftraf_get_of_counts(self):
        """Gets the openFlow packets counts, measured by oftraf. It uses the
        oftraf rest apy and returns the result as a string in JSON format
        :returns: oftraf metrics as string in JSON format
        :rtype: str
        :raises oftraf_exceptions.OftrafError: if execution of handler fails
        """
        try:
            try:
                getheaders = {'Accept': 'application/json'}
                url = \
                    'http://{0}:{1}/get_of_counts'.format(
                        self.rest_server_ip, self.rest_server_port)
                s = requests.Session()
                s.trust_env = False
                req = s.get(url, headers=getheaders, stream=False)
                return req.content.decode('utf-8')
            except:
                raise(stress_test.oftraf_exceptions.OftrafGetResultError(
                    'Fail getting total number of installed flows \n Oftraf '
                    'REST request status code: {0} \n Oftraf REST request '
                    'data: {1}'.format(req.status_code,
                                       req.content.decode('utf-8'))))
        except stress_test.oftraf_exceptions.OftrafError as e:
            self.error_handling(e.err_msg, e.err_code)

    def __del__(self):
        """Method called when object is destroyed"""
        try:
            logging.info('Run oftraf stop.')
            self.stop()
        except:
            pass

        try:
            logging.info('Run oftraf cleanup.')
            self.clean()
        except:
            pass

        try:
            logging.info('Close oftraf node ssh connection.')
            self._ssh_conn.close()
        except:
            pass