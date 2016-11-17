# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Controller Class- All controller-related functionality is here"""

import logging
import os
import sys
import stress_test.controller_exceptions
import time
import util.file_ops
import util.netutil
import util.process
import queue


class Controller:

    def __init__(self, ctrl_base_dir, test_config):

        """Create a Controller object. Options from JSON input file
        :param test_config: JSON input configuration
        :param ctrl_base_dir: controller base directory
        :type test_config: JSON configuration dictionary
        :type ctrl_base_dir: str
        """
        self.name = test_config['controller_name']
        self.base_dir = ctrl_base_dir

        self.ip = test_config['controller_node_ip']
        self.ssh_port = test_config['controller_node_ssh_port']
        self.ssh_user = test_config['controller_node_username']
        self.ssh_pass = test_config['controller_node_password']

        self.need_rebuild = test_config['controller_rebuild']
        self.need_cleanup = test_config['controller_cleanup']
        self.of_port = test_config['controller_port']
        self.logs_dir = self.base_dir + test_config['controller_logs_dir']

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
        util.file_ops.check_filelist([self.build_hnd,
                                      self.start_hnd,
                                      self.stop_hnd,
                                      self.status_hnd,
                                      self.clean_hnd])

    @staticmethod
    def new(ctrl_base_dir, test_config):
        """ Factory method. Creates a subclass class depending on the
        controller name
        :returns: a subclass or None
        :rtype: failed_flow_ops int
        """
        name = test_config['controller_name']
        if (name == 'odl'):
            return ODL(ctrl_base_dir, test_config)

        elif name == 'onos':
            raise NotImplementedError('ONOS is not supported yet')
        #  return ONOS(ctrl_base_dir, test_config)

        else:
            raise NotImplementedError('Not supported yet')
        #   return None

    def error_handling(self, error_message, error_num=1):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error('{0} :::::::::: Exception :::::::::::'.
                      format(exc_obj))
        logging.error(error_message)
        logging.error('Error number:{0}'.format(error_num))
        logging.error('{0} - {1} Exception: {2}, {3}'.
                      format(exc_obj, self.name, exc_type, exc_tb.tb_lineno))
        # Propagate error outside the class to stop execution
        raise(stress_test.controller_exceptions.CtrlError)

    def init_ssh(self):
        """Initializes a new SSH client object, with the controller node and
        stores it to the protected variable _ssh_conn. If a connection already
        exists it returns a new SSH client object to the controller node.
        """
        logging.info(
            '[open_ssh_connection] Initiating SSH session with {0} node.'.
            format(self.name, self.ip))
        try:
            try:
                if self._ssh_conn is None:
                    self._ssh_conn = util.netutil.ssh_connect_or_return2(
                        self.ip, int(self.ssh_port), self.ssh_user,
                        self.ssh_pass, 10)
                else:
                    # Return a new client ssh object for the controller node
                    return util.netutil.ssh_connect_or_return2(
                        self.ip, int(self.ssh_port), self.ssh_user,
                        self.ssh_pass, 10)
            except:
                raise(stress_test.controller_exceptions.CtrlNodeConnectionError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def cleanup(self):
        """Wrapper to the controller cleanup handler
        """
        try:
            try:
                logging.info('[Controller] Cleaning up')

                self.status = 'CLEANING'
                util.netutil.ssh_run_command(self._ssh_conn,
                                             self.clean_hnd,
                                             '[controller.clean_handler]')[0]
                self.status = 'CLEANED'
            except:
                raise(stress_test.controller_exceptions.CtrlCleanupError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def check_status(self):
        """Wrapper to the controller status handler
        """
        logging.info('[Controller] Checking the status')
        try:
            try:
                q = queue.Queue()
                util.netutil.ssh_run_command(self._ssh_conn, self.status_hnd,
                                             '[controller.status_handler]', q)[0]
                cmd_output = ''
                while not q.empty():
                    cmd_output += str(q.get()) + ' '
                if cmd_output.strip() == '1':
                    logging.info('[Controller] status: Running-'
                                 ' {0}'.format(cmd_output))
                elif cmd_output.strip() == '0':
                    logging.info('[Controller] status: Not'
                                 'Running- {0}'.format(cmd_output))
                return cmd_output.strip()
            except:
                raise(stress_test.controller_exceptions.CtrlStatusUnknownError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def check_other_controller(self):
        """Checks for processes listening on the specified port
        :raises Exception: when another process listens on controller's port.
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
                    raise(stress_test.controller_exceptions.CtrlPortConflictError(
                        '[check_other_controller] Another process is '
                        'active on port {0}'.format(self.of_port), 2))
            except stress_test.controller_exceptions.CtrlError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlPortConflictError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def restart(self):
        """Restarts the controller
        :rtype: int
        """
        logging.info('[Controller] Restarting')

        self.status = 'RESTARTING'
        self.stop()
        self.pid = self.start()
        self.status = 'RESTARTED'

    def start(self):
        """Wrapper to the controller start handler
        :raises Exception: When controller fails to start.
        """
        logging.info('[Controller] Starting')
        try:
            try:
                self.status = 'STARTING'
                if self._ssh_conn is None:
                    os.environ['JAVA_OPTS'] = self.java_opts
                    cmd = [self.start_hnd]
                else:
                    cmd = ['export JAVA_OPTS="{0}";'.format(self.java_opts),
                           self.start_hnd]
                if self.check_status() == '0':
                    exit_status, cmd_output = util.netutil.ssh_run_command(
                        self._ssh_conn, ' '.join(cmd),
                        '[controller.start_handler]')
                    self.pid = self.wait_until_listens(420000)
                    logging.info('[start_controller] Controller '
                                 'pid: {0}'.format(self.pid))
                    self.wait_until_up(420000)
                    if exit_status != 0 or self.pid == -1:
                        raise(stress_test.controller_exceptions.CtrlStartError(
                            '[start_controller] Fail to start: {0}'.
                            format(cmd_output), 2))
                elif self.check_status() == '1':
                    logging.info('[start_controller] Controller already '
                                 'started.')
                self.status = 'STARTED'
            except stress_test.controller_exceptions.CtrlError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlStartError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def stop(self):
        """Wrapper to the controller stop handler
        """

        try:
            try:
                self.status = 'STOPPING'
                if self.check_status() == '1':
                    logging.info('[Controller] Stopping. Controller PID: {0}'.
                                 format(self.pid))
                    exit_status, cmd_output = util.netutil.ssh_run_command(
                        self._ssh_conn, ' '.join([self.stop_hnd]),
                        '[controller.stop_handler]')
                    util.process.wait_until_process_finishes(self.pid,
                                                             self._ssh_conn)
                    if exit_status != 0:
                        raise(stress_test.controller_exceptions.CtrlStopError(
                            '{Controller] Controller failed to stop: {0}'.
                            format(cmd_output)))
                    self.status = 'STOPPED'
                else:
                    logging.info('[stop_controller] Controller already '
                                 'stopped.')
            except stress_test.controller_exceptions.CtrlError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlStopError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def build(self):
        """ Wrapper to the controller build handler
        """
        logging.info('[Controller] Building')
        try:
            try:
                self.status = 'BUILDING'
                exit_status, cmd_output = util.netutil.ssh_run_command(
                    self._ssh_conn, ' '.join([self.build_hnd]),
                    '[controller.build_handler]')
                if exit_status == 0:
                    self.status = 'BUILT'
                    logging.info("[Controller] Successful building")
                else:
                    self.status = 'NOT_BUILT'
                    raise(stress_test.controller_exceptions.CtrlBuildError(
                        '[Controller] Failure during building: {0}'.
                        format(cmd_output)), 2)
            except stress_test.controller_exceptions.CtrlError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlBuildError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def wait_until_listens(self, timeout_ms):
        """ Waits for controller to start listening on specified port.
        :param timeout_ms: milliseconds to wait (in milliseconds).
        :raises Exception: If controller fails to start or if another process
        listens on controllers port.
        :rtype int
        :type timeout_ms: int
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
                        raise(stress_test.controller_exceptions.CtrlPortConflictError(
                            'Another controller seems to have started in the '
                            'meantime. Exiting...'))

                raise (stress_test.controller_exceptions.CtrlReadyStateError(
                    'Controller failed to start within a period of {0} '
                    'minutes'.format(timeout), 2))
            except stress_test.controller_exceptions.CtrlError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlReadyStateError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def wait_until_up(self, timeout_ms):
        """ Waits for controller status to become 1 (started).

        :param timeout_ms: milliseconds to wait (in milliseconds).
        :raises Exception: If controller fails to start or if another process
        listens on controllers port.
        :type timeout_ms: int
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
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.controller_exceptions.CtrlReadyStateError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def __del__(self):
        """Method called when object is destroyed"""
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

    def __init__(self, ctrl_base_dir, test_config):

        super(self.__class__, self).__init__(ctrl_base_dir, test_config)

        # The parameters initialized as None are dimensions of the test.
        # These values are passed outside, from the test in the main for loop.
        # ---------------------------------------------------------------------
        self.stat_period_ms = None
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
        """ Starts and then stops the controller to trigger the generation of
        controller's XML files.
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
            self.error_handling(e.err_msg, e.err_code)

    def disable_persistence(self):
        """configure controller persistent to false in order not to backup
        datastore on the disk.
        """
        logging.info('[Controller] Disabling persistence')
        try:
            try:
                util.netutil.ssh_run_command(self._ssh_conn,
                                             ' '.join([self.persistence_hnd]),
                                             '[controller.change'
                                             '_persistent_handler]')
            except:
                raise(stress_test.controller_exceptions.ODLDisablePersistenceError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def change_stats(self):
        """Wrapper to the controller statistics handler
        """

        logging.info('[Controller] Changing statistics period')
        try:
            try:
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
            self.error_handling(e.err_msg, e.err_code)

    def flowmods_config(self):
        """configure controller to send flow modifications as a
        response to ARP Packet_INs.
        """
        logging.info('[Controller] Configure flow modifications')
        try:
            try:
                util.netutil.ssh_run_command(self._ssh_conn,
                                             ' '.join([self.flowmods_conf_hnd]),
                                             '[controller.flowmod'
                                             '_configure_handler]')[0]
                logging.info('[Controller] Controller is configured to '
                             'send flow mods')
            except:
                raise(stress_test.controller_exceptions.ODLFlowModConfError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def get_oper_hosts(self, new_ssh_conn=None):
        """Wrapper to the controller oper_hosts handler
        """
        logging.info('[Controller] Query number of hosts '
                     'registered in ODL operational DS')
        try:
            try:
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
                    '[controller.operational_hosts_handler]')[1]
                if new_ssh_conn is not None:
                    used_ssh_conn.close()
                return int(ret)
            except:
                raise(stress_test.controller_exceptions.ODLGetOperHostsError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def get_oper_switches(self, new_ssh_conn=None):
        """Wrapper to the controller oper_switches handler
        """
        logging.info('[Controller] Query number of switches '
                     ' registered in ODL operational DS')
        try:
            try:
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
                    '[controller.operational switches_handler]')[1]
                if new_ssh_conn is not None:
                    used_ssh_conn.close()
                return int(ret)
            except:
                raise(stress_test.controller_exceptions.ODLGetOperSwitchesError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def get_oper_links(self, new_ssh_conn=None):
        """Wrapper to the controller oper_links handler
        """
        logging.info('[Controller] Query number of links registered in '
                     ' ODL operational DS')
        try:
            try:
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
                    '[controller.operational_links_handler]')[1]
                if new_ssh_conn is not None:
                    used_ssh_conn.close()
                return int(ret)
            except:
                raise(stress_test.controller_exceptions.ODLGetOperLinksError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)

    def get_oper_flows(self, new_ssh_conn=None):
        """Wrapper to the controller oper_flows handler
        """
        logging.info('[Controller] Query number of flows installed for '
                     'all installed nodes of the topology')
        try:
            try:
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
                return int(ret)
            except:
                raise(stress_test.controller_exceptions.ODLGetOperFlowsError)
        except stress_test.controller_exceptions.CtrlError as e:
            self.error_handling(e.err_msg, e.err_code)


class ONOS(Controller):

    def __init__(self, ctrl_base_dir, test_config):

        super(self.__class__, self).__init__(ctrl_base_dir, test_config)

        self.stat_period_ms = test_config['controller_statistics_period_ms']

        self.oper_hosts = -1
        self.oper_switches = -1
        self.oper_links = -1
        self.oper_flows = -1
