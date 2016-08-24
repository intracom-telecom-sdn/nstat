# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Controller Class- All controller-related functionality is here"""

import json
import common
import logging
import os
import subprocess
import time
import util.netutil
import util.process
import conf_collections_util
import requests
import emulators.nb_generator.flow_utils



class Controller:


    def __init__(self, ctrl_base_dir, test_config):

        """Create a Controller object. Options from JSON input file
        :param test_config: JSON input configuration
        :type test_config: JSON configuration dictionary
        """
        self.name = test_config['controller_name']
        logging.info('Initializing parameters for the {0} Controller '.format(self.name))

        self.base_dir = ctrl_base_dir
        self.ip = test_config['controller_node_ip']
        self.ssh_port = test_config['controller_node_ssh_port']
        self.username = test_config['controller_node_username']
        self.password = test_config['controller_password']

        self.need_rebuild = self.base_dir + test_config['controller_rebuild']
        self.need_cleanup = self.base_dir + test_config['controller_cleanup']
        self.of_port = test_config['controller_port']
        self.cpu_shares = test_config['controller_cpu_shares']
        self.logs_dir = self.base_dir + test_config['controller_logs_dir']

        self.build_hnd = self.base_dir + test_config['controller_build_handler']
        self.start_hnd = self.base_dir + test_config['controller_start_handler']
        self.stop_hnd = self.base_dir + test_config['controller_stop_handler']
        self.status_hnd = self.base_dir + test_config['controller_status_handler']
        self.clean_hnd = self.base_dir + test_config['controller_clean_handler']

        self.status = 'UNKNOWN'

        self.java_opts = ' '.join(test_config['java_opts'])
        self.pid = -1

        self._init_ssh = None

        self_node = conf_collections_util.node_parameters(self.name,
                                      self.ip,
                                      int(self.ssh_port),
                                      self.username,
                                      self.password)

    def init_ssh(self)
        logging.info(
            '[open_ssh_connection] Initiating SSH session with {0} node.'.
            format(self.name))
        self._init_ssh = util.netutil.ssh_connect_or_return(connection, 10)



    def cleanup(self):
        """Wrapper to the controller cleanup handler
        """
        logging.info('[Controller] Cleaning up')

        self.status = 'CLEANING'
        common.command_exec_wrapper([self.clean_hnd],
                                    '[controller.clean_handler]', self._init_ssh)
        self.status = 'CLEANED'

    def check_status(self):
        """Wrapper to the controller status handler
        """
        logging.info('[Controller] Checking the status')

        common.command_exec_wrapper([self.status_hnd],


    def check_other_controller(self):
        """Checks for processes listening on the specified port

        :raises Exception: when another process listens on controller's port.
        """

        logging.info(
            '[Controller] Checking if another process is '
            'listening on specified port. Port number: {0}.'.
            format(self.of_port))

        # check if any process listens on controller port
        gpid = util.process.getpid_listeningonport(self.of_port, self._init_ssh)

        if gpid != -1:
            raise Exception('[check_other_controller] Another process is '
                            'active on port {0}'.
                            format(self.of_port))

    def restart(self):
        """Restarts the controller
        :rtype: int
        """
        logging.info('[Controller] Restarting')

        self.status = 'RESTARTING'
        self.stop()
        self.status = 'STOPPED'
        self.pid = self.start(controller_cpus)
        self.status = 'STARTED'

    def start(self, controller_cpus):
        """Wrapper to the controller start handler

        :param controller_cpus: number of cpus returned by create_cpu_shares() and
        allocated for controller
        :raises Exception: When controller fails to start.
        :rtype: int
        :type controller_cpus: str
        """
        logging.info('[Controller] Starting')

        self.status = 'STARTING'
        if self._init_ssh==None:
            os.environ['JAVA_OPTS'] = self.java_opts
            cmd = [self.start_hnd]
        else:
            cmd = ['export JAVA_OPTS="{0}";'.format(self.java_opts),
                   'taskset', '-c', '{0}'.format(controller_cpus),
                   self.start_hnd]
        logging.info('[set_java_opts] JAVA_OPTS set to {0}'.format(self.java_opts))

        if check_status() == '0':
            common.command_exec_wrapper(cmd, '[controller_start_handler]', self._init_ssh)
            logging.info(
                '[start_controller] Waiting until controller starts listening')
            self.pid = self.wait_until_listens(420000)
            logging.info('[start_controller] Controller pid: {0}'.format(self.pid))
            logging.info(
                '[start_controller] Checking controller status after it starts '
                'listening on port {0}.'.format(self.of_port))
            self.wait_until_up(420000)
        else:
            logging.info('[start_controller] Controller already started.')

        self.status = 'STARTED'

    def stop():
        """Wrapper to the controller stop handler
        """

        self.status = 'STOPPING'
        if check_status() == '1':
            logging.info('[stop_controller] Stopping controller.')
            common.command_exec_wrapper(
                [self.stop_hnd],
                '[controller_stop_handler]', self._init_ssh)
            util.process.wait_until_process_finishes(self.pid, self._init_ssh)
        else:
            logging.info('[stop_controller] Controller already stopped.')

        self.status = 'STOPPED'

    def build(self):
        """ Wrapper to the controller build handler
        """
        logging.info('[Controller] Building')
        self.status = 'BUILDING'

        common.command_exec_wrapper([self.build_hnd],
                             '[controller_build_handler]', self._init_ssh)

        self.status = 'BUILT'

    def wait_until_listens(interval_ms):
        """ Waits for controller to start listening on specified port.

        :param interval_ms: milliseconds to wait (in milliseconds).
        :raises Exception: If controller fails to start or if another process
        listens on controllers port.
        :rtype int
        :type interval_ms: int
        """

        logging.info('[Controller] Waiting to start listening on a port')

        timeout = time.time() + (float(interval_ms) / 1000)
        while time.time() < timeout:
            time.sleep(1)
            gpid = util.process.getpid_listeningonport(self.port, self._init_ssh)
            logging.info('Returned pid listening on port {0}: {1}'.
                          format(self.port, gpid))
            if gpid == 0:
                raise Exception('Another controller seems to have started in the '
                                'meantime. Exiting...')

        raise Exception('Controller failed to start within a period of {0} '
                        'minutes'.format(timeout))


    def wait_until_up(interval_ms):
        """ Waits for controller status to become 1 (started).

        :param interval_ms: milliseconds to wait (in milliseconds).
        :raises Exception: If controller fails to start or if another process
        listens on controllers port.
        :type interval_ms: int
        """

        logging.info('[Controller] Waiting to be started')

        timeout = time.time() + (float(interval_ms) / 1000)
        while time.time() < timeout:
            time.sleep(1)
            if check_status() == '1':
                return

        raise Exception('Controller failed to start. '
                        'Status check returned 0 after trying for {0} seconds.'.
                        format(float(interval_ms) / 1000))



class ODL(Controller):

    def __init__(self, ctrl_base_dir, test_config):

        super(self.__class__, self).__init__(ctrl_base_dir, test_config)

        self.stat_period_ms = test_config['controller_statistics_period_ms']

        if 'controller_flowmods_conf_handler' in test_config:
            self.flowmods_conf_hnd= ctrl_base_dir + test_config['controller_flowmods_conf_handler']

        if 'controller_statistics_handler' in test_config:
            self.statistics_hnd = ctrl_base_dir + test_config['controller_statistics_handler']

        if 'controller_persistent_handler' in test_config:
            self.persistent_hnd = ctrl_base_dir + test_config['controller_persistent_handler']

        if 'controller_restconf_port' in test_config:
            self.restconf_port = test_config['controller_restconf_port']
            self.restconf_user = test_config['controller_restconf_user']
            self.restconf_password = test_config['controller_restconf_password']

        self.hosts = -1
        self.switches = -1
        self.links = -1
        self.flows = -1


    def generate_xmls(self, controller_cpus):
        """ Starts and then stops the controller to trigger the generation of
        controller's XML files.

        :param controller_cpus: number of cpus returned by create_cpu_shares() and
        allocated for controller
        :type controller_cpus: str
        """
        logging.info('[Controller] Generating XMLs')
        pid = self.start(controller_cpus)

        # Controller status check is done within start()
        logging.info('Controller status is 1.')
        logging.info('[generate_xmls] Stopping controller')
        self.stop()



    def disable_persistence(self):
        """configure controller persistent to false in order not to backup
        datastore on the disk.
        """
        logging.info('[controller] Disabling persistent')

        common.command_exec_wrapper([self.persistent_hnd],
                                    '[controller_change_persistent_handler]',
                                    self._init_ssh)


    def change_stats(self):
        """Wrapper to the controller statistics handler
        """

        logging.info('[controller] Changing statistics period')
        common.command_exec_wrapper(
            [self.statistics_hnd, str(stat_period_ms)],
            '[controller.statistics_handler] Changing statistics interval',
            self._init_ssh)
        logging.info(
            '[change_stats] Changed statistics period to {0} ms'.
            format(self.stat_period_ms))


    def flowmods_config(self):
        """configure controller to send flow modifications as a responce to ARP
        Packet_INs.
        """
        logging.info('[controller] Configure flow modifications')
        common.command_exec_wrapper([self.flowmods_conf_hnd],
                                    '[controller_flowmod_configure_handler]',
                                    self._init_ssh)


    def get_oper_hosts(self):
        """Query number of hosts registered in ODL operational DS
        """

        logging.info('[Controller] Getting the number of operational hosts')

        url = ('http://{0}:{1}/restconf/operational/network-topology:'
               'network-topology/network-topology:topology/flow:1/'.
               format(self.ip, self.restconf_port))

        auth_token = (self.restconf_username,
                      self.restconf_password)
        try:
            datastore = requests.get(url=url,
                auth=auth_token).json()['topology'][0]
        except:
            self.hosts = -1

        get_hosts = l[node for node in datastore.get('node', []) if node['node-id'].startswith('host:')]
        self.hosts = len(get_hosts)

    def get_oper_switches(self):
        """Query number of switches registered in ODL operational DS
        """

        logging.info('[Controller] Getting the number of operational switches')
        url = ('http://{0}:{1}/restconf/operational/network-topology:'
               'network-topology/network-topology:topology/flow:1/'.
               format(self.ip, self.restconf_port))

        auth_token = (self.restconf_username,
                      self.restconf_password)

        logging.debug('[check_ds_switches] Making RestCall: {0}'.format(url))

        try:
            datastore = requests.get(url=url,
                auth=auth_token).json()['topology'][0]

        except:
            logging.error('[check_ds_switches] Fail getting response from '
                          'operational datastore')

            self.switches = -1

        get_switches = [node for node in datastore.get('node', []) if not node['node-id'].startswith('host:')]

        self.switches = len(get_switches)

        logging.debug('[check_ds_switches] Discovered switches: {0}'.
                      format(self.switches))

    def get_oper_links(self):
        """Query number of links registered in ODL operational DS
        """

        logging.info('[Controller] Getting the number of operational switches')

        url = ('http://{0}:{1}/restconf/operational/network-topology:'
               'network-topology/network-topology:topology/flow:1/'.
               format(self.ip, self.restconf_port))
        auth_token = (self.restconf_username,
                      self.restconf_password)
        try:
            datastore = requests.get(url=url,
                auth=auth_token).json()['topology'][0]
        except:
            self.links = -1

        get_links = [link for link in datastore.get('link', [])]
        self.links = len(get_links)


    def get_oper_flows(self):
        """Query number of flows in ODL operational DS
        """
        logging.info('[Controller] Getting the number of operational flows')

        odl_inventory = emulators.nb_generator.flow_utils.FlowExplorer(self.ip,
                                                             self.restconf_port,
                                                             'operational',
                                                             (self.restconf_username, self.restconf_.password))
        odl_inventory.get_inventory_flows_stats()
        logging.debug('Found {0} flows at inventory'.
                      format(odl_inventory.found_flows))

        self.flows = odl_inventory.found_flows