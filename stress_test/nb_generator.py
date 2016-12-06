# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NB-Generator Class- All NB-Generator-related functionality is here"""

# import emulators.nb_generator
import gevent
import logging
import stress_test.nb_generator_exceptions
import sys
import time
import traceback
import util.netutil


class NBgen:

    def __init__(self, nb_gen_base_dir, test_config, controller, sbemu,
                 log_level="DEBUG"):
        """Create an NB-generator object. Options from JSON input file
        :param test_config: JSON input configuration
        :param nb_gen_base_dir: emulator base directory
        :param controller: object of the Controller class
        :param sbemu: object of the SBEmu subclass
        :type test_config: JSON configuration dictionary
        :type nb_gen_base_dir: str
        :type controller: object
        :type sbemu: object
        """
        self.controller = controller
        self.sbemu = sbemu
        self.name = test_config['nb_emulator_name']
        self.base_dir = nb_gen_base_dir
        self.traceback_enabled = False

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
        self.flows_discovery_deadline = 240

        self.confirm_time = 0.0
        self.e2e_installation_time = 0.0
        self.discover_flows_on_switches_time = 0.0

        self.venv_hnd = self.base_dir + "bin/venv_handler.sh"

    def error_handling(self, error_message, error_num=1):
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
        logging.info(
            '[open_ssh_connection] Initiating SSH session with {0} node on '
            '{1} host.'.format(self.name, self.ip))
        try:
            try:
                if self._ssh_conn is None:
                    self._ssh_conn = util.netutil.ssh_connect_or_return2(
                        self.ip, int(self.ssh_port), self.ssh_user,
                        self.ssh_pass, 10)
                else:
                    # Return a new client ssh object for the nb-generator node
                    return util.netutil.ssh_connect_or_return2(
                        self.ip, int(self.ssh_port), self.ssh_user,
                        self.ssh_pass, 10)
            except:
                raise(stress_test.nb_generator_exceptions.NBGenNodeConnectionError)
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self.error_handling(e.err_msg, e.err_code)

    def build(self):
        """ Wrapper to the NB-Generator build handler
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[NB_generator] Building')
        self.status = 'BUILDING'

        exit_status = util.netutil.ssh_run_command(self._ssh_conn,
                                                   ' '.join([self.build_hnd]),
                                                   '[NB_generator.'
                                                   'build_handler]')[0]
        if exit_status == 0:
            self.status = 'BUILT'
            logging.info("[NB_generator] Successful building")
        else:
            self.status = 'NOT_BUILT'
            raise Exception('[NB_generator] Failure during building')

    def clean(self):
        """Wrapper to the NB-Generator clean handler
        :raises: Exception if the handler does not exist on the remote host
        :raises: Exception if the exit status of the handler is not 0
        """
        logging.info('[NB_generator] Cleaning')
        self.status = 'CLEANING'

        exit_status = util.netutil.ssh_run_command(self._ssh_conn,
                                                   self.clean_hnd,
                                                   '[NB_generator.'
                                                   'clean_handler]')[0]
        if exit_status == 0:
            self.status = 'CLEANED'
            logging.info("[NB_generator] Successful clean")
        else:
            self.status = 'NOT_CLEANED'
            raise Exception('[NB_generator] Failure during cleaning')

    def run(self):
        """ Wrapper to the NB-Generator run handler
        :returns: Returns the combined stdout - stderr of the executed command
        :rtype: str
        """
        logging.info("[NB_generator] Run handler")
        self.status = 'STARTED'
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.run_hnd]):
                    raise(IOError(
                        '[NB_generator] Run handler does not exist'))

                print(' '.join([str(self.venv_hnd),
                                str(self.base_dir),
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
                                str(self.log_level)]))
                '''
                exit_status, cmd_output = \
                    util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([str(self.venv_hnd),
                                                   str(self.base_dir),
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
                                                 '[NB_generator] run_handler]')
                '''
                exit_status, cmd_output = \
                    util.netutil.ssh_run_command(
                        self._ssh_conn,
                        ' '.join(["python3.4",
                                  str(self.run_hnd),
                                  str(self.controller.ip),
                                  str(self.controller.restconf_port),
                                  str(self.total_flows),
                                  str(self.flow_workers),
                                  str(self.flow_operations_delay_ms),
                                  str(self.flow_delete_flag),
                                  str(self.controller.restconf_user),
                                  str(self.controller.restconf_pass),
                                  int(self.flows_per_request),
                                  str(self.log_level)]),
                        '[NB_generator] run_handler]')

                if exit_status == 0:
                    self.status = 'NB_GEN_RUNNING'
                    logging.info("[NB_generator] up and running")
                else:
                    self.status = 'NB_GEN_NOT_RUNNING'
                    raise(stress_test.nb_generator_exceptions.NBGenRunError(
                        '[NB_generator] Failure during running. {0}'.
                        format(cmd_output), 2))
                print("cmd_output:")
                a = type(cmd_output)
                print(cmd_output)
                print(a)
                return cmd_output
            except stress_test.nb_generator_exceptions.NBGenError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.nb_generator_exceptions.NBGenRunError)
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self.error_handling(e.err_msg, e.err_code)

    def get_oper_ds_flows(self):
        """ Wrapper to the NB-Generator get operational DS flows handler
        :returns: Returns the combined stdout - stderr of the executed command
        :rtype: str
        """
        logging.info("[NB_generator] get_oper_ds_flows handler")
        try:
            try:
                if not util.netutil.isfile(self.ip, self.ssh_port,
                                           self.ssh_user, self.ssh_pass,
                                           [self.run_hnd]):
                    raise(IOError(
                        '[NB_generator] get_oper_ds_flows handler does '
                        'not exist'))

                    print(str(self.venv_hnd),
                          str(self.base_dir),
                          str(self.get_oper_ds_flows_hnd),
                          str(self.controller.ip),
                          str(self.controller.restconf_port),
                          str(self.controller.restconf_user),
                          str(self.controller.restconf_pass))

                exit_status, cmd_output = \
                    util.netutil.ssh_run_command(self._ssh_conn,
                                                 ' '.join([str(self.venv_hnd),
                                                 str(self.base_dir),
                                                 str(self.get_oper_ds_flows_hnd),
                                                 str(self.controller.ip),
                                                 str(self.controller.restconf_port),
                                                 str(self.controller.restconf_user),
                                                 str(self.controller.restconf_pass)]),
                                                 '[NB_generator] '
                                                 'get_oper_ds_flows handler]')
                print("************************************************")
                print("cmd_output:")
                print(cmd_output)
                print("exit_status:")
                print(exit_status)
                print("************************************************")
                print("************************************************")
                if exit_status == 0:
                    logging.info("[NB_generator] up and running")
                else:
                    raise(stress_test.nb_generator_exceptions.NBGenRunError(
                        '[NB_generator] Failure during getting the flows from'
                        'operational DS . {0}'.
                        format(cmd_output), 2))
                return cmd_output
            except stress_test.nb_generator_exceptions.NBGenError as e:
                self.error_handling(e.err_msg, e.err_code)
            except:
                raise(stress_test.nb_generator_exceptions.NBGenRunError)
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self.error_handling(e.err_msg, e.err_code)

    def __poll_flows_ds(self, t_start):
        """
        Monitors operational DS from the time the transmission starts from NB
        towards the controller until the expected number of flows are
        found or the deadline is reached.
        :param t_start: timestamp for begin of discovery
        :returns: Returns a float number containing the time in which
        total flows were discovered otherwise containing -1.0 on failure.
        :rtype: float
        :type t_start: float
        """
        try:
            try:
                t_discovery_start = time.time()
                previous_discovered_flows = 0
                while True:
                    if (time.time() - t_discovery_start) > \
                            self.flows_discovery_deadline:
                        logging.info('[NB_generator] [Poll_flows thread] '
                                     'Deadline of {0} seconds passed'
                                     .format(self.flows_discovery_deadline))
                        self.e2e_installation_time = -1.0
                        logging.info('[NB_generator] [Poll_flows thread] End '
                                     'to End installation time monitor FAILED')
                        return
                    else:
                        new_ssh = self.controller.init_ssh()
                        oper_ds_found_flows = self.controller.get_oper_flows(
                            new_ssh)
                        logging.debug('[NB_generator] [Poll_flows_ thread] '
                                      'Found {0} flows at inventory'.
                                      format(oper_ds_found_flows))
                        if (oper_ds_found_flows - previous_discovered_flows) != 0:
                            t_discovery_start = time.time()
                            previous_discovered_flows = oper_ds_found_flows
                        if oper_ds_found_flows == self.total_flows:
                            time_interval = time.time() - t_start
                            logging.debug('[NB_generator] [Poll_flows thread] '
                                          'Flow-Master {0} flows found in {1}'
                                          ' seconds'
                                          .format(self.total_flows,
                                                  time_interval))
                            self.e2e_installation_time = time_interval
                            logging.info('[NB_generator] [Poll_flows thread] '
                                         'End to End installation time is: {0}'
                                         .format(self.e2e_installation_time))
                            return
                    gevent.sleep(1)
            except:
                raise(stress_test.nb_generator_exceptions.NBGenPollDSError(
                    'Error in end to end datastore flow polling.'))
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self.error_handling(e.err_msg, e.err_code)

    def __poll_flows_ds_confirm(self):
        """
        Monitors operational DS until the expected number of flows are found
        or the deadline is reached.
        :returns: Returns a float number containing the time in which
        total flows were discovered otherwise containing -1.0 on failure.
        :rtype: float
        """
        try:
            try:
                t_start = time.time()
                t_discovery_start = time.time()
                previous_discovered_flows = 0
                while True:
                    if (time.time() - t_discovery_start) > \
                            self.flows_discovery_deadline:
                        logging.info('[NB_generator] '
                                     '[Poll_flows_confirm thread] Deadline '
                                     'of {0} seconds passed'
                                     .format(self.flows_discovery_deadline))
                        self.confirm_time = -1.0
                        logging.info('[NB_generator] '
                                     '[Poll_flows_confirm thread] '
                                     'Confirmation time monitoring FAILED')
                        return
                    else:
                        new_ssh = self.controller.init_ssh()
                        oper_ds_found_flows = \
                            self.controller.get_oper_flows(new_ssh)
                        logging.debug('[NB_generator] '
                                      '[Poll_flows_confirm thread] Found {0} '
                                      'flows at inventory'
                                      .format(oper_ds_found_flows))
                        if (oper_ds_found_flows - previous_discovered_flows) != 0:
                            t_discovery_start = time.time()
                            previous_discovered_flows = oper_ds_found_flows
                        if oper_ds_found_flows == self.total_flows:
                            time_interval = time.time() - t_start
                            logging.debug('[NB_generator] '
                                          '[Poll_flows_confirm thread] '
                                          'Flow-Master {0} flows found in {1}'
                                          ' seconds'.format(self.total_flows,
                                                            time_interval))
                            self.confirm_time = time_interval
                            logging.info('[NB_generator] [Poll_flows_confirm '
                                         'thread] Confirmation time is: {0}'
                                         .format(self.confirm_time))
                            return
                    gevent.sleep(1)
            except:
                raise(stress_test.nb_generator_exceptions.NBGenPollDSError(
                    'Error in flow confirm datastore flow polling.'))
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self.error_handling(e.err_msg, e.err_code)

    def __poll_flows_switches(self, t_start):
        """
        Monitors installed flows into switches of Multinet from the first REST
        request, until the expected number of flows are found or the deadline
        is reached.
        :param t_start: timestamp for beginning of discovery
        :returns: Returns a float number containing the time in which
        total flows were discovered in Multinet switches. Otherwise containing
        -1.0 on failure.
        :rtype: float
        :type t_start: float
        """
        try:
            try:
                t_discovery_start = time.time()
                previous_discovered_flows = 0
                while True:
                    if (time.time() - t_discovery_start) > \
                            self.flows_discovery_deadline:
                        logging.info('[NB_generator] '
                                     '[Poll_flows_switches thread] '
                                     'Deadline of {0} seconds passed'
                                     .format(self.flows_discovery_deadline))
                        self.discover_flows_on_switches_time = -1.0
                        logging.info('[NB_generator] '
                                     '[Poll_flows_switches thread] '
                                     'Discovering flows on switches FAILED')
                        return
                    else:
                        new_ssh = self.sbemu.init_ssh()
                        discovered_flows = self.sbemu.get_flows(new_ssh)
                        logging.debug('[NB_generator] '
                                      '[Poll_flows_switches thread] '
                                      'Found {0} flows at topology switches'
                                      .format(discovered_flows))
                        if (discovered_flows - previous_discovered_flows) != 0:
                            t_discovery_start = time.time()
                            previous_discovered_flows = discovered_flows
                        if discovered_flows == self.total_flows:
                            time_interval = time.time() - t_start
                            logging.debug('[NB_generator] '
                                          '[Poll_flows_switches thread]'
                                          ' expected flows = {0} \n '
                                          'discovered flows = {1}'
                                          .format(self.total_flows,
                                                  discovered_flows))
                            self.discover_flows_on_switches_time = time_interval
                            logging.info('[NB_generator] '
                                         '[Poll_flows_switches thread] '
                                         'Time to discover flows on switches '
                                         'is: {0}'.format(self.discover_flows_on_switches_time))
                            return
                    gevent.sleep(1)
            except:
                raise(stress_test.nb_generator_exceptions.NBGenPollOVSError(
                    'Error during discovery on flows installed directly on '
                    'Topology Switches (OpenVSwitch polling).'))
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self.error_handling(e.err_msg, e.err_code)

    def monitor_threads_run(self, t_start):
        """
        Monitors operational flows in switches of Multinet until the expected
        number of flows are found or the deadline is reached.
        :param t_start: timestamp for begin of discovery
        :returns: Returns a float number containing the time in which
        total flows were discovered otherwise containing -1.0 on failure.
        :rtype: float
        :type t_start:
        """
        logging.info('[NB_generator] Start polling measurements')
        try:
            try:
                monitor_ds = gevent.spawn(self.__poll_flows_ds, t_start)
                monitor_sw = gevent.spawn(self.__poll_flows_switches, t_start)
                monitor_ds_confirm = gevent.spawn(self.__poll_flows_ds_confirm)
                gevent.joinall([monitor_ds, monitor_sw, monitor_ds_confirm])

                time_start = time.time()
                discovered_flows = self.sbemu.get_flows()
                flow_measurement_latency_interval = time.time() - time_start
                logging.info('[NB_generator] Flows measurement latency '
                             'interval: {0} sec. | Discovered flows: {1}'
                             .format(flow_measurement_latency_interval,
                                     discovered_flows))
            except:
                raise(stress_test.nb_generator_exceptions.NBGenMonitorRunError)
        except stress_test.nb_generator_exceptions.NBGenError as e:
            self.error_handling(e.err_msg, e.err_code)

    def __del__(self):
        """Method called when object is destroyed"""
        try:
            logging.info('Closing NB-Generator ssh connection.')
            self._ssh_conn.close()
        except:
            pass
