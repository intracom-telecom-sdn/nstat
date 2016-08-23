# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Controller Class- All controller-related functionality is here"""

#import collections
import json
import common
import logging
import os
import subprocess
import time
import util.netutil
import util.process



class Controller:




    def __init__(self,ctrl_base_dir,test_config):

#        logging.info('[Controller Class] Parsing test configuration')
#        with open(json_file) as json_conf_file:
#        self.test_config = json.load(json_conf_file)

        """Create a Controller object. Options from JSON input file
        :param test_config: JSON input configuration
        :type test_config: JSON configuration dictionary
        """
        self.__dict__ = test_config
        self.name = test_config['controller_name']
        logging.info('Initializing parameters for the {0} Controller '.format(self.name))

        #self.host_ip = test_config['controller_host_ip']
        self.node_ip = test_config['controller_node_ip']
        self.node_ssh_port = test_config['controller_node_ssh_port']
        self.node_username = test_config['controller_node_username']
        self.node_password = test_config['controller_password']

        self.logs_dir = ctrl_base_dir + test_config['controller_logs_dir']
        self.rebuild = ctrl_base_dir + test_config['controller_rebuild']
        self.cleanup = ctrl_base_dir + test_config['controller_cleanup']
        self.port = test_config['controller_port']
        self.statistics_period_ms = test_config['controller_statistics_period_ms']
        self.cpu_shares = test_config['controller_cpu_shares']
        self.logs_dir = ctrl_base_dir + test_config['controller_logs_dir']

        self.build_handler = ctrl_base_dir + test_config['controller_build_handler']
        self.start_handler = ctrl_base_dir + test_config['controller_start_handler']
        self.stop_handler = ctrl_base_dir + test_config['controller_stop_handler']
        self.status_handler = ctrl_base_dir + test_config['controller_status_handler']
        self.clean_handler = ctrl_base_dir + test_config['controller_clean_handler']
        self.statistics_handler = ctrl_base_dir + test_config['controller_statistics_handler']
        self.persistent_handler = ctrl_base_dir + test_config['controller_persistent_handler']


        self.java_opts = ' '.join(test_config['java_opts'])
        self.cpid = -1

    def cleanup(self,ssh_client=None):
        """Wrapper to the controller cleanup handler

        :param self.clean_handler: filepath to the controller cleanup handler
        :param ssh_client : SSH client provided by paramiko to run the command
        :type self.clean_handler: str
        :type ssh_client: paramiko.SSHClient
        """
        common.command_exec_wrapper([self.clean_handler],
                                    '[self.clean_handler]', ssh_client)

    def change_persistent_controller(controller_change_persistent_handler,
                                     ssh_client=None):
        """configure controller persistent to false in order not to backup
        datastore on the disk.

        :param ssh_client : SSH client provided by paramiko to run the command
        :type ssh_client: paramiko.SSHClient
        """

        common.command_exec_wrapper([self.persistent_handler],
                                    '[controller_change_persistent_handler]',
                                    ssh_client)

    def check_controller_status(self,ssh_client=None):
        """Wrapper to the controller status handler

        :param self.status_handler: filepath to the controller status handler
        :param ssh_client : SSH client provided by paramiko to run the command
        :returns: '1' if controller is active, '0' otherwise
        :rtype: str
        :type self.status_handler: str
        :type ssh_client: paramiko.SSHClient
        """

        if ssh_client == None:
            return subprocess.check_output([self.status_handler],
                                        universal_newlines=True).strip()
        else:
            cmd_output = util.netutil.ssh_run_command(ssh_client,
                self.status_handler)[1]
            return cmd_output.strip()

    def check_for_active_controller(self,ssh_client=None):
        """Checks for processes listening on the specified port

        :param self.port: controller port to check
        :param ssh_client : paramiko SSH client object when opening a connection
        :raises Exception: when another process listens on controller's port.
        :type self.port: int
        :type ssh_client: paramiko.SSHClient
        """

        logging.info(
            '[check_for_active_controller] Checking if another process is '
            'listening on specified port. Port number: {0}.'.
            format(self.port))

        # check if any process listens on controller port
        gpid = util.process.getpid_listeningonport(self.port, ssh_client)

        if gpid != -1:
            raise Exception('[check_for_active_controller] Another process is '
                            'active on port {0}'.
                            format(self.port))

    def controller_pre_actions(self, controller_ssh_client, controller_cpus):
        """ Performs all necessary actions before starting a test. Pre actions
        are 1) rebuild_controller 2) check_for_active_controller
        3) generate_controller_xml_files

        :param controller_ssh_client: paramiko.SSHClient object
        :param controller_cpus: number of cpus returned by create_cpu_shares() and
        allocated for controller
        :type controller_ssh_client: paramiko.SSHClient
        :type controller_cpus: str
        """
        if self.controller_rebuild:
            logging.info('[controller_pre_actions] building controller')
            rebuild_controller(self.build_handler, controller_ssh_client)

        logging.info('[controller_pre_actions] checking for other active '
                     'controllers')
        check_for_active_controller(controller_ssh_client)
        logging.info('[controller_pre_actions] starting and stopping controller'
                     ' to generate xml files')
        self.generate_controller_xml_files(controller_ssh_client, controller_cpus)
        if self.persistent_handler != '':
            change_persistent_controller(
                self.persistent_handler,
                controller_ssh_client)


    def generate_controller_xml_files(self, ssh_client, controller_cpus):
        """ Starts and then stops the controller to trigger the generation of
        controller's XML files.

        :param ssh_client : SSH client provided by paramiko to run the command
        :param controller_cpus: number of cpus returned by create_cpu_shares() and
        allocated for controller
        :type ssh_client: paramiko.SSHClient
        :type controller_cpus: str
        """
        logging.info('[generate_controller_xml_files] Starting controller')
        cpid = start_controller(controller_cpus, ssh_client)

        # Controller status check is done within start_controller()
        logging.info('[generate_controller_xml_files] OK, controller status is 1.')
        logging.info('[generate_controller_xml_files] Stopping controller')
        stop_controller(ssh_client)


    def rebuild_controller(self, ssh_client=None):
        """ Wrapper to the controller build handler

        :param ssh_client : SSH client provided by paramiko to run the command
        :type ssh_client: paramiko.SSHClient
        """

        common.command_exec_wrapper([self.build_handler],
                             '[controller_build_handler]', ssh_client)


    def restart_controller(self,ssh_client=None):
        """Restarts the controller

        :param ssh_client : SSH client provided by paramiko to run the command
        :rtype: int
        :type ssh_client: paramiko.SSHClient
        """

        stop_controller(ssh_client)
        self.cpid = start_controller(controller_cpus,ssh_client)

    def start_controller(self, controller_cpus, ssh_client=None):
        """Wrapper to the controller start handler

        :param controller_cpus: number of cpus returned by create_cpu_shares() and
        allocated for controller
        :param ssh_client : SSH client provided by paramiko to run the command
        :raises Exception: When controller fails to start.
        :rtype: int
        :type controller_cpus: str
        :type ssh_client: paramiko.SSHClient
        """

        if ssh_client==None:
            os.environ['JAVA_OPTS'] = self.java_opts
            cmd = [self.start_handler]
        else:
            cmd = ['export JAVA_OPTS="{0}";'.format(self.java_opts),
                   'taskset', '-c', '{0}'.format(controller_cpus),
                   self.start_handler]
        logging.info('[set_java_opts] JAVA_OPTS set to {0}'.format(self.java_opts))

        if check_controller_status(ssh_client) == '0':
            common.command_exec_wrapper(cmd, '[controller_start_handler]', ssh_client)
            logging.info(
                '[start_controller] Waiting until controller starts listening')
            self.cpid = wait_until_controller_listens(420000, ssh_client)
            logging.info('[start_controller] Controller pid: {0}'.format(self.cpid))
            logging.info(
                '[start_controller] Checking controller status after it starts '
                'listening on port {0}.'.format(self.controller_port))
            wait_until_controller_up_and_running(420000, ssh_client)
        else:
            logging.info('[start_controller] Controller already started.')


    def stop_controller(ssh_client=None):
        """Wrapper to the controller stop handler

        :param ssh_client : SSH client provided by paramiko to run the command
        :type ssh_client: paramiko.SSHClient
        """

        if check_controller_status(ssh_client) == '1':
            logging.info('[stop_controller] Stopping controller.')
            common.command_exec_wrapper(
                [self.stop_handler],
                '[controller_stop_handler]', ssh_client)
            util.process.wait_until_process_finishes(self.cpid, ssh_client)
        else:
            logging.info('[stop_controller] Controller already stopped.')


    def wait_until_controller_listens(interval_ms, ssh_client=None):
        """ Waits for controller to start listening on specified port.

        :param interval_ms: milliseconds to wait (in milliseconds).
        :param ssh_client : SSH client provided by paramiko to run the command
        :raises Exception: If controller fails to start or if another process
        listens on controllers port.
        :rtype int
        :type interval_ms: int
        :type ssh_client: paramiko.SSHClient
        """

        timeout = time.time() + (float(interval_ms) / 1000)
        while time.time() < timeout:
            time.sleep(1)
            gpid = util.process.getpid_listeningonport(self.port, ssh_client)
            logging.info('Returned pid listening on port {0}: {1}'.
                          format(self.port, gpid))
            if gpid == 0:
                raise Exception('Another controller seems to have started in the '
                                'meantime. Exiting...')

        raise Exception('Controller failed to start within a period of {0} '
                        'minutes'.format(timeout))


    def wait_until_controller_up_and_running(interval_ms, ssh_client=None):
        """ Waits for controller status to become 1 (started).

        :param interval_ms: milliseconds to wait (in milliseconds).
        :param controller_status_handler: filepath to the controller status handler
        :raises Exception: If controller fails to start or if another process
        listens on controllers port.
        :type interval_ms: int
        :type ssh_client: paramiko.SSHClient
        """

        timeout = time.time() + (float(interval_ms) / 1000)
        while time.time() < timeout:
            time.sleep(1)
            if check_controller_status(ssh_client) == '1':
                return

        raise Exception('Controller failed to start. '
                        'Status check returned 0 after trying for {0} seconds.'.
                        format(float(interval_ms) / 1000))



class ODL(Controller):
    def __init__(self,ctrl_base_dir,test_config):
        Controller.__init__(self,test_config)
        stat_period_ms = test_config['controller_statistics_period_ms']

        if 'controller_flowmods_conf_handler' in test_config:
           flowmods_conf_handler= ctrl_base_dir + test_config['controller_flowmods_conf_handler']




    def controller_changestatsperiod(self,
                                 ssh_client=None):
        """Wrapper to the controller statistics handler

        :param self.statistics_handler: filepath to the controller statistics
        handler
        :param stat_period_ms: statistics period value to set (in milliseconds)
        :param ssh_client : SSH client provided by paramiko to run the command
        :type self.statistics_handler: str
        :type curr_stat_period: int
        :type ssh_client: paramiko.SSHClient
        """
        common.command_exec_wrapper(
            [self.statistics_handler, str(stat_period_ms)],
            '[self.statistics_handler] Changing statistics interval',
            ssh_client)
        logging.info(
            '[controller_changestatsperiod] Changed statistics period to {0} ms'.
            format(stat_period_ms))


    def flowmod_configure_controller(ssh_client=None):
        """configure controller to send flow modifications as a responce to ARP
        Packet_INs.

        :param ssh_client : SSH client provided by paramiko to run the command
        :type ssh_client: paramiko.SSHClient
        """

        common.command_exec_wrapper([self.flowmods_conf_handler],
                                    '[controller_flowmod_configure_handler]',
                                    ssh_client)