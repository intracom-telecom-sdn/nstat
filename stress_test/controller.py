# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import os
import sys
import stress_test.controller_exceptions
import time
import traceback
import util.file_ops
import util.netutil
import util.process
import queue


class Controller:
    """
    All controller-related functionality is here
    """

    def __init__(self, ctrl_base_dir, test_config):

        """
        Creates a Controller object. Options from JSON input file

        :param test_config: JSON input configuration
        :param ctrl_base_dir: controller base directory
        :type test_config: JSON configuration dictionary
        :type ctrl_base_dir: str
        """
        self.name = test_config['controller_name']
        self.base_dir = ctrl_base_dir

        self.traceback_enabled = False
        self.ip = test_config['controller_node_ip']
        self.ssh_port = test_config['controller_node_ssh_port']
        self.ssh_user = test_config['controller_node_username']
        self.ssh_pass = test_config['controller_node_password']

        self.need_cleanup = test_config['controller_cleanup']
        self.of_port = test_config['controller_port']
        self.logs_dir = self.base_dir + test_config['controller_logs_dir']

        self.get_hnd = (self.base_dir +
                          test_config['controller_get_handler'])
        self.build_hnd = (self.base_dir +
                          test_config['controller_build_handler'])
        self.start_hnd = (self.base_dir +
                          test_config['controller_start_handler'])
        self.stop_hnd = (self.base_dir +
                         test_config['controller_stop_handler'])
        self.status_hnd = (self.base_dir +
                           test_config['controller_status_handler'])
        self.clean_hnd = (self.base_dir +
                          test_config['controller_clean_handler'])

        self.status = 'UNKNOWN'

        self.java_opts = ' '.join(test_config['java_opts'])
        self.pid = -1

        self._ssh_conn = None

        # check handlers' validity
        '''util.file_ops.check_filelist([self.build_hnd,
                                      self.start_hnd,
                                      self.stop_hnd,
                                      self.status_hnd,
                                      self.clean_hnd])
        '''
        # NSTAT Controller dirs contain only build/clean handlers

        util.file_ops.check_filelist([self.build_hnd,
                                      self.clean_hnd])

    @staticmethod
    def new(ctrl_base_dir, test_config):
        """
        Factory method. Creates a subclass class depending on the
        controller name

        :returns: a subclass or None
        :rtype: object
        :raises NotImplementedError: in case an invalid controller_name is \
            given in the configuration json file
        """
        name = test_config['controller_name']
        if (name == 'ODL'):
            return ODL(ctrl_base_dir, test_config)

        elif name == 'ONOS':
            raise NotImplementedError('ONOS is not supported yet')
        #  return ONOS(ctrl_base_dir, test_config)

        else:
            raise NotImplementedError('Not supported yet')
        #   return None

    def _error_handling(self, error_message, error_num=1):
        """
        Handles custom errors of controller

        :param error_message: message of the handled error
        :param error_num: error number of the handled error, used to define \
            subcases of raised errors.
        :type error_message: str
        :type error_num: int
        :raises controller_exceptions.CtrlError: to terminate execution of
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
        # Propagate error outside the class to stop execution of test
        raise(stress_test.controller_exceptions.CtrlError)

    def init_ssh(self):
        """
        Initializes a new SSH client object, with the controller node and \
            assigns it to the protected attribute _ssh_conn. If a connection \
            already exists it returns a new SSH client object to the  \
            controller node.

        :raises controller_exceptions.CtrlNodeConnectionError: if ssh \
            connection establishment fails
        """
        logging.info(
            '[open_ssh_connection] Initiating SSH session with {0} node.'.
            format(self.name, self.ip))
        try:
            try:
                if self._ssh_conn is None:
                    self._ssh_conn = util.netutil.ssh_connect_or_return(
                        self.ip, int(self.ssh_port), self.ssh_user,
                        self.ssh_pass, 10)
                else:
                    # Return a new client ssh object for the controller node
                    return util.netutil.ssh_connect_or_return(
                        self.ip, int(self.ssh_port), self.ssh_user,
                        self.ssh_pass, 10)
            except:
                raise(stress_test.controller_exceptions.
                      CtrlNodeConnectionError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def cleanup(self):
        """
        Wrapper to the controller cleanup handler

        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.CtrlCleanupError: if controller cleanup \
            handler fails
        """
        logging.info('[Controller] Cleaning up')
        self.status = 'CLEANING'
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.clean_hnd]):
                    self.status = 'NOT_CLEANED'
                    raise(IOError(
                        '{0} clean handler does not exist'.
                        format('[controller.cleanup]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.clean_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, self.clean_hnd,
                    '[controller.clean_handler]')
                if exit_status == 0:
                    self.status = 'CLEANED'
                    logging.info('[controller.clean_handler] controller '
                                 'successfully cleaned.')
                else:
                    self.status = 'NOT_CLEANED'
                    raise(stress_test.controller_exceptions.CtrlCleanupError(
                        '[controller.clean_handler] controller cleanup '
                        'handler exited with non zero exit status. \n '
                        'Handler output: {0}'.format(cmd_output), exit_status))
            except stress_test.controller_exceptions.CtrlError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlCleanupError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def check_status(self):
        """
        Wrapper to the controller status handler

        :returns: the status of the controller (running = 1, not running = 0)
        :rtype: int
        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.CtrlStatusUnknownError: if the handler \
            fails to return controller status or fails to execute
        """
        logging.info('[Controller] Checking the status')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.status_hnd]):
                    raise(IOError(
                        '{0} status handler does not exist'.
                        format('[controller.status]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.status_hnd)
                q = queue.Queue()
                util.netutil.ssh_run_command(self._ssh_conn, self.status_hnd,
                                             '[controller.status]', q)
                cmd_output = ''
                while not q.empty():
                    cmd_output += str(q.get()) + ' '
                if cmd_output.strip() == '1':
                    logging.info('[controller.status]: Running-'
                                 ' {0}'.format(cmd_output))
                elif cmd_output.strip() == '0':
                    logging.info('[controller.status]: Not'
                                 'Running- {0}'.format(cmd_output))
                else:
                    raise(stress_test.controller_exceptions.
                          CtrlStatusUnknownError(
                              '[controller.status_handler] Error while '
                              'fetching status of the controller. Invalid '
                              'value returned./n Returned status value: {0}'.
                              format(cmd_output.strip()), 2))
                return cmd_output.strip()
            except:
                raise(stress_test.controller_exceptions.CtrlStatusUnknownError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def check_other_controller(self):
        """
        Checks for processes listening on the specified port

        :raises controller_exceptions.CtrlPortConflictError: when another \
            process listens on controller's port.
        """

        logging.info(
            '[Controller] Checking if another process is '
            'listening on specified port. Port number: {0}.'.
            format(self.of_port))
        try:
            try:
                # check if any process listens on controller port
                gpid = util.process.getpid_listeningonport(self.of_port,
                                                           self._ssh_conn)
                if gpid != -1:
                    raise(stress_test.controller_exceptions.
                          CtrlPortConflictError(
                              '[check_other_controller] Another process is '
                              'active on port {0}'.format(self.of_port), 2))
            except stress_test.controller_exceptions.CtrlError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.
                      CtrlPortConflictError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def restart(self):
        """
        Restarts the controller
        """
        logging.info('[Controller] Restarting')

        self.status = 'RESTARTING'
        self.stop()
        self.start()
        self.status = 'RESTARTED'

    def start(self):
        """
        Wrapper to the controller start handler

        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.CtrlStartError: When controller fails to \
            start.
        """
        logging.info('[Controller.start] Starting')
        self.status = 'STARTING'
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.start_hnd]):
                    self.status = 'NOT_STARTED'
                    raise(IOError(
                        '{0} start handler does not exist'.
                        format('[controller.stop]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.start_hnd)
                if self._ssh_conn is None:
                    os.environ['JAVA_OPTS'] = self.java_opts
                    cmd = [self.start_hnd]
                else:
                    cmd = ['export JAVA_OPTS="{0}";'.format(self.java_opts),
                           self.start_hnd]
                if self.check_status() == '0':
                    exit_status, cmd_output = util.netutil.ssh_run_command(
                        self._ssh_conn, ' '.join(cmd),
                        '[Controller.start]')
                    self.pid = self.wait_until_listens(420000)
                    logging.info('[Controller.start] Controller '
                                 'pid: {0}'.format(self.pid))
                    self.wait_until_up(420000)
                    if exit_status != 0 or self.pid == -1:
                        self.status = 'NOT_STARTED'
                        raise(stress_test.controller_exceptions.CtrlStartError(
                            '[Controller.start] Fail to start. Start handler '
                            'exited with non zero exit status. \n '
                            'Handler output: {0}'.format(cmd_output),
                            exit_status))
                elif self.check_status() == '1':
                    logging.info('[Controller.start] Controller already '
                                 'started.')
                self.status = 'STARTED'
            except stress_test.controller_exceptions.CtrlError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlStartError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def stop(self):
        """
        Wrapper to the controller stop handler

        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.CtrlStopError: if controller fails to \
            stop successfully
        """
        self.status = 'STOPPING'
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.stop_hnd]):
                    self.status = 'NOT_STOPED'
                    raise(IOError(
                        '{0} stop handler does not exist'.
                        format('[controller.stop]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.stop_hnd)
                if self.check_status() == '1':
                    logging.info('[Controller.stop] Stopping. Controller '
                                 'PID: {0}'.format(self.pid))
                    exit_status, cmd_output = util.netutil.ssh_run_command(
                        self._ssh_conn, ' '.join([self.stop_hnd]),
                        '[controller.stop]')
                    util.process.wait_until_process_finishes(self.pid,
                                                             self._ssh_conn)
                    if exit_status == 0:
                        self.status = 'STOPPED'
                        logging.info("[Controller.stop] Successful stopped")
                    else:
                        self.status = 'NOT_STOPPED'
                        raise(stress_test.controller_exceptions.CtrlStopError(
                            '[Controller.stop] Controller failed to stop: {0}'.
                            format(cmd_output), exit_status))
                else:
                    self.status = 'STOPPED'
                    logging.info('[Controller.stop] Controller already '
                                 'stopped.')
            except stress_test.controller_exceptions.CtrlError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlStopError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)


    def getcontroller(self):
        """
        Wrapper to the get controller handler

        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.CtrlGetError: if get controller process
            fails
        """
        logging.info('[Controller] Downloading...')
        self.status = 'BUILDING'
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.get_hnd]):
                    self.status = 'NOT_BUILT'
                    raise(IOError(
                        '{0} get controller handler does not exist'.
                        format('[controller.build]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.get_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join([self.get_hnd]),
                    '[controller.get]')
                if exit_status == 0:
                    self.status = 'BUILT'
                    logging.info("[Controller.get] Successfully downloaded")
                else:
                    self.status = 'NOT_BUILT'
                    raise(stress_test.controller_exceptions.CtrlGetError(
                        '[Controller.get] Failure during controller download. '
                        'Get handler exited with non zero exit status. \n '
                        'Handler output: {0}'.
                        format(cmd_output)), exit_status)
            except stress_test.controller_exceptions.CtrlError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlGetError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def build(self):
        """
        Wrapper to the controller build handler

        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.CtrlBuildError: if build process fails
        """
        logging.info('[Controller] Building')
        self.status = 'BUILDING'
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.build_hnd]):
                    self.status = 'NOT_BUILT'
                    raise(IOError(
                        '{0} build handler does not exist'.
                        format('[controller.build]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.build_hnd)
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join([self.build_hnd]),
                    '[controller.build]')
                if exit_status == 0:
                    self.status = 'BUILT'
                    logging.info("[Controller.build] Successful building")
                else:
                    self.status = 'NOT_BUILT'
                    raise(stress_test.controller_exceptions.CtrlBuildError(
                        '[Controller.build] Failure during building. Build '
                        'handler exited with non zero exit status. \n '
                        'Handler output: {0}'.
                        format(cmd_output)), exit_status)
            except stress_test.controller_exceptions.CtrlError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlBuildError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def wait_until_listens(self, timeout_ms):
        """
        Waits for controller to start listening on specified port.

        :param timeout_ms: milliseconds to wait (in milliseconds).
        :returns: the process ID PID of the controller.
        :rtype: int
        :type timeout_ms: int
        :raises controller_exceptions.CtrlReadyStateError: If controller \
            fails to start
        :raises controller_exceptions.CtrlPortConflictError: if another \
            process listens on controllers port.
        """

        logging.info('[Controller] Waiting to start listening on a port')
        try:
            try:
                timeout = time.time() + (float(timeout_ms) / 1000)
                while time.time() < timeout:
                    time.sleep(1)
                    gpid = util.process.getpid_listeningonport(self.of_port,
                                                               self._ssh_conn)
                    logging.info('[Controller] Returned pid listening '
                                 'on port {0}: {1}'.format(self.of_port, gpid))
                    if gpid > 0:
                        return gpid
                    elif gpid == 0:
                        raise(stress_test.controller_exceptions.
                              CtrlPortConflictError(
                                  'Another controller seems to have started '
                                  'in the meantime. Exiting...'))

                raise (stress_test.controller_exceptions.CtrlReadyStateError(
                    'Controller failed to start within a period of {0} '
                    'seconds'.format(float(timeout_ms) / 1000), 2))
            except stress_test.controller_exceptions.CtrlError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlReadyStateError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def wait_until_up(self, timeout_ms):
        """
        Waits for controller status to become 1 (started).

        :param timeout_ms: milliseconds to wait (in milliseconds).
        :type timeout_ms: int
        :raises controller_exceptions.CtrlReadyStateError: If controller fails \
             to reach a ready state within a certain period of time.
        """

        logging.info('[Controller] Waiting to be started')
        try:
            try:
                timeout = time.time() + (float(timeout_ms) / 1000)
                while time.time() < timeout:
                    time.sleep(1)
                    if self.check_status() == '1':
                        logging.info('[Controller] Started')
                        return
                raise(stress_test.controller_exceptions.CtrlReadyStateError(
                    'Controller failed to start. Status check returned 0 '
                    'after trying for {0} seconds.'.
                    format(float(timeout_ms) / 1000), 2))
            except stress_test.controller_exceptions.CtrlError as e:
                self._error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlReadyStateError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def __del__(self):
        """
        Method called when object is destroyed. Cleanup activities are
        triggered and open connections closed
        """
        try:
            logging.info('Run controller stop.')
            self.stop()
        except:
            pass

        try:
            logging.info('Run controller cleanup.')
            self.cleanup()
        except:
            pass

        try:
            logging.info('Close controller node ssh connection.')
            self._ssh_conn.close()
        except:
            pass


class ODL(Controller):
    """
    All OpenDaylight controller-related functionality is here
    """

    def __init__(self, ctrl_base_dir, test_config):
        """
        Initialize the creation of an OpenDaylight controller object.
        Inherits from Controller class.

        :param ctrl_base_dir: emulator base directory
        :param test_config: JSON input configuration
        :type ctrl_base_dir: str
        :type test_config: JSON configuration dictionary
        """
        super(self.__class__, self).__init__(ctrl_base_dir, test_config)

        # The parameters initialized as None are dimensions of the test.
        # These values are passed outside, from the test in the main for loop.
        # ---------------------------------------------------------------------
        self.stat_period_ms = None
        self.build()
        # ---------------------------------------------------------------------
        if 'controller_flowmods_conf_handler' in test_config:
            self.flowmods_conf_hnd = \
                ctrl_base_dir + test_config['controller_flowmods_conf_handler']

            # check handler's validity
            util.file_ops.check_filelist([self.flowmods_conf_hnd])

        if 'controller_statistics_handler' in test_config:
            self.statistics_hnd = \
                ctrl_base_dir + test_config['controller_statistics_handler']

            # check handler's validity
            util.file_ops.check_filelist([self.statistics_hnd])

        if 'controller_persistent_handler' in test_config:
            self.persistence_hnd = \
                ctrl_base_dir + test_config['controller_persistent_handler']

            # check handler's validity
            util.file_ops.check_filelist([self.persistence_hnd])

        if 'controller_restconf_port' in test_config:
            self.restconf_port = test_config['controller_restconf_port']
            self.restconf_user = test_config['controller_restconf_user']
            self.restconf_pass = test_config['controller_restconf_password']

        self.oper_hosts = (ctrl_base_dir +
                           test_config['controller_oper_hosts_handler'])
        self.oper_switches = (ctrl_base_dir +
                              test_config['controller_oper_switches_handler'])
        self.oper_links = (ctrl_base_dir +
                           test_config['controller_oper_links_handler'])
        self.oper_flows = (ctrl_base_dir +
                           test_config['controller_oper_flows_handler'])

    def generate_xmls(self):
        """
        Starts and then stops the controller to trigger the generation of \
            controller's XML files.

        :raises controller_exceptions.ODLXMLError: if generation of XML files \
            fails
        """
        logging.info('[Controller] Generating XML files'
                     ' (start and stop the Controller)')
        try:
            try:
                self.start()
                self.stop()
            except:
                raise(stress_test.controller_exceptions.ODLXMLError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def disable_persistence(self):
        """
        Configure controller persistent to false in order not to backup \
            datastore on the disk.

        :raises controller_exceptions.ODLDisablePersistenceError: if disable \
            of persistence fails
        """
        logging.info('[Controller] Disabling persistence')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.persistence_hnd]):
                    raise(IOError(
                        '{0} disable_persistence handler does not exist'.
                        format('[controller.disable_persistence]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.persistence_hnd)
                util.netutil.ssh_run_command(self._ssh_conn,
                                             ' '.join([self.persistence_hnd]),
                                             '[controller.disable_persistence]'
                                             )
            except:
                raise(stress_test.controller_exceptions.
                      ODLDisablePersistenceError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def change_stats(self):
        """
        Wrapper to the controller statistics handler. Changes the value of \
            statistics interval in the configuration files of controller.

        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.ODLChangeStats: if change of statistics \
            interval fails
        """
        logging.info('[Controller] Changing statistics period')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.statistics_hnd]):
                    raise(IOError(
                        '{0} statistics handler does not exist'.
                        format('[controller.change_stats]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.statistics_hnd)
                util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join([self.statistics_hnd,
                                              str(self.stat_period_ms)]),
                    '[controller.statistics_handler]'
                    ' Changing statistics interval')
                logging.info(
                    '[Controller] Changed statistics period to {0} ms'.
                    format(self.stat_period_ms))
            except:
                raise(stress_test.controller_exceptions.ODLChangeStats)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def flowmods_config(self):
        """
        Configure controller to send flow modifications as a response to ARP \
            ARP Packet_INs.

        :raises controller_exceptions.ODLFlowModConfError: if configuration \
            actions to respond with flow modifications fail.
        """
        logging.info('[Controller.flowmods_config] Configure flow '
                     'modifications')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.flowmods_conf_hnd]):
                    raise(IOError(
                        '{0} Configure for FlowMods handler does not exist'.
                        format('[controller.flowmods_config]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.flowmods_conf_hnd)
                util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join([self.flowmods_conf_hnd]),
                    '[controller.flowmods_config]')[0]
                logging.info('[Controller.flowmods_config] Controller is '
                             'configured to send flow mods')
            except:
                raise(stress_test.controller_exceptions.ODLFlowModConfError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def get_oper_hosts(self, new_ssh_conn=None):
        """
        Wrapper to the controller oper_hosts handler. Makes a REST call to \
            the NB interface of the controller and returns the number of hosts \
            of the topology, recorded in operational datastore of the controller

        :param new_ssh_conn: an ssh connection client object
        :returns: number of hosts from controller's operational datastore
        :type new_ssh_conn: paramiko.SSHClient
        :rtype: int
        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.ODLGetOperHostsError: if handler fails \
            to run or return a valid value
        """
        logging.info('[Controller] Query number of hosts '
                     'registered in ODL operational DS')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.oper_hosts]):
                    raise(IOError(
                        '{0} get_oper_hosts handler does not exist'.
                        format('[controller.get_oper_hosts]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.oper_hosts)
                if new_ssh_conn is not None:
                    used_ssh_conn = new_ssh_conn
                else:
                    used_ssh_conn = self._ssh_conn
                ret = util.netutil.ssh_run_command(
                    used_ssh_conn, ' '.join([self.oper_hosts,
                                             str(self.ip),
                                             str(self.restconf_port),
                                             str(self.restconf_user),
                                             str(self.restconf_pass)]),
                    '[controller.get_oper_hosts]')[1]
                if new_ssh_conn is not None:
                    used_ssh_conn.close()
                try:
                    return int(ret)
                except:
                    return -1
            except:
                raise(stress_test.controller_exceptions.ODLGetOperHostsError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def get_oper_switches(self, new_ssh_conn=None):
        """
        Wrapper to the controller oper_switches handler. Makes a REST call \
            to the NB interface of the controller and returns the number of \
            switches of the topology, recorded in operational datastore of the \
            controller

        :param new_ssh_conn: an ssh connection client object
        :returns: number of switches from controller's operational datastore
        :type new_ssh_conn: paramiko.SSHClient
        :rtype: int
        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.ODLGetOperSwitchesError:  if handler \
            fails to run or return a valid value
        """
        logging.info('[Controller] Query number of switches '
                     ' registered in ODL operational DS')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.oper_switches]):
                    raise(IOError(
                        '{0} get_oper_switches handler does not exist'.
                        format('[controller.get_oper_switches]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.oper_switches)
                if new_ssh_conn is not None:
                    used_ssh_conn = new_ssh_conn
                else:
                    used_ssh_conn = self._ssh_conn
                ret = util.netutil.ssh_run_command(
                    used_ssh_conn, ' '.join([self.oper_switches,
                                             str(self.ip),
                                             str(self.restconf_port),
                                             str(self.restconf_user),
                                             str(self.restconf_pass)]),
                    '[controller.get_oper_switches]')[1]
                if new_ssh_conn is not None:
                    used_ssh_conn.close()
                try:
                    return int(ret)
                except:
                    return -1
            except:
                raise(stress_test.controller_exceptions.
                      ODLGetOperSwitchesError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def get_oper_links(self, new_ssh_conn=None):
        """
        Wrapper to the controller oper_links handler. Makes a REST call \
            to the NB interface of the controller and returns the number of \
            links of the topology, recorded in operational datastore of the \
            controller

        :param new_ssh_conn: an ssh connection client object
        :returns: number of links from controller's operational datastore
        :type new_ssh_conn: paramiko.SSHClient
        :rtype: int
        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.ODLGetOperLinksError: if handler \
            fails to run or return a valid value
        """
        logging.info('[Controller] Query number of links registered in '
                     ' ODL operational DS')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.oper_links]):
                    raise(IOError(
                        '{0} get_oper_links handler does not exist'.
                        format('[controller.get_oper_links]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.oper_links)
                if new_ssh_conn is not None:
                    used_ssh_conn = new_ssh_conn
                else:
                    used_ssh_conn = self._ssh_conn
                ret = util.netutil.ssh_run_command(
                    used_ssh_conn, ' '.join([self.oper_links,
                                             str(self.ip),
                                             str(self.restconf_port),
                                             str(self.restconf_user),
                                             str(self.restconf_pass)]),
                    '[controller.get_oper_links]')[1]
                if new_ssh_conn is not None:
                    used_ssh_conn.close()
                try:
                    return int(ret)
                except:
                    return -1
            except:
                raise(stress_test.controller_exceptions.ODLGetOperLinksError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def get_oper_flows(self, new_ssh_conn=None):
        """
        Wrapper to the controller oper_flows handler. Makes a REST call \
            to the NB interface of the controller and returns the number of \
            flows of the topology, recorded in operational datastore of the \
            controller

        :param new_ssh_conn: an ssh connection client object
        :returns: number of flows from controller's operational datastore
        :type new_ssh_conn: paramiko.SSHClient
        :rtype: int
        :raises IOError: if the handler does not exist on the remote host
        :raises controller_exceptions.ODLGetOperFlowsError: if handler \
            fails to run or return a valid value
        """
        logging.info('[Controller] Query number of flows installed for '
                     'all installed nodes of the topology')
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.oper_flows]):
                    raise(IOError(
                        '{0} get_oper_flows handler does not exist'.
                        format('[controller.get_oper_links]')))
                else:
                    util.netutil.make_remote_file_executable(
                        self.ip, self.ssh_port, self.ssh_user, self.ssh_pass,
                        self.oper_flows)
                if new_ssh_conn is not None:
                    used_ssh_conn = new_ssh_conn
                else:
                    used_ssh_conn = self._ssh_conn
                ret = util.netutil.ssh_run_command(
                    used_ssh_conn, ' '.join([self.oper_flows,
                                             str(self.ip),
                                             str(self.restconf_port),
                                             str(self.restconf_user),
                                             str(self.restconf_pass)]),
                    '[controller.operational_flows_handler]')[1]
                if new_ssh_conn is not None:
                    used_ssh_conn.close()
                try:
                    return int(ret)
                except:
                    return -1
            except:
                raise(stress_test.controller_exceptions.ODLGetOperFlowsError)
        except stress_test.controller_exceptions.CtrlError as e:
            self._error_handling(e.err_msg, e.err_code)

    def save_log(self, output_dir):
        """
        Save controller log file

        :param output_dir: the directory where the controller logs are stored
        :type output_dir: str
        """
        # Move controller log file if exist inside the test output dir
        try:
            logging.info('[controller_save_log] collecting logs from '
                         'controller node. Logs path:{0}'.
                         format(self.logs_dir))
            util.netutil.copy_dir_remote_to_local(
                self.ip,
                self.ssh_port,
                self.ssh_user,
                self.ssh_pass,
                os.path.join(self.base_dir, self.logs_dir),
                os.path.join(output_dir, 'log'))
        except:
            logging.error('[controller_save_log] Fail transferring controller'
                          ' logs directory.')


class ONOS(Controller):
    """
    All ONOS controller-related functionality is here
    """
    def __init__(self, ctrl_base_dir, test_config):
        """
        Initialize the creation of an ONOS controller object.
        Inherits from Controller class.

        :param ctrl_base_dir: emulator base directory
        :param test_config: JSON input configuration
        :type ctrl_base_dir: str
        :type test_config: JSON configuration dictionary
        """
        super(self.__class__, self).__init__(ctrl_base_dir, test_config)

        self.stat_period_ms = test_config['controller_statistics_period_ms']

        self.oper_hosts = -1
        self.oper_switches = -1
        self.oper_links = -1
        self.oper_flows = -1
