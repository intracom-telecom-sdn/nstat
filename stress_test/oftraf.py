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
import util.netutil


class Oftraf:

    def __init__(self, controller, test_config):
        """Create an Oftraf Monitor Controller object.
        Options from JSON input file
        :param controller: object of the Controller class
        :param test_config: JSON input configuration
        :type controller: object
        """

        if 'oftraf_test_interval_ms' in test_config:
            self.interval_ms = test_config['oftraf_test_interval_ms']
        self.rest_server_port = test_config['oftraf_rest_server_port']
        self.rest_server_ip = controller.ip
        self.status = 'UNKNOWN'
        self._ssh_conn = controller.init_ssh()

    def get_oftraf_path(self):
        """Returns oftraf base directory path relatively to the project path
        """
        stress_test_base_dir = os.path.abspath(os.path.join(
            os.path.realpath(__file__), os.pardir))
        monitors_base_dir = os.path.abspath(os.path.join(stress_test_base_dir,
                                                         os.pardir))
        print("FLAG")
        oftraf_path = os.path.sep.join(
            [monitors_base_dir, 'monitors', 'oftraf', ''])
        print(oftraf_path)
        return str(oftraf_path)

    def build(self):
        """ Wrapper to the oftraf monitor build handler
        """
        oftraf_path = self.get_oftraf_path
        print(oftraf_path)
        build_hnd = str(oftraf_path) + 'build.sh'
        logging.info('[Oftraf] Building')
        self.status = 'BUILDING'

        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([build_hnd]),
                                         '[oftraf.build_handler]')[0]
        if exit_status == 0:
            self.status = 'BUILT'
            logging.info("[Oftraf] Successful building")
        else:
            self.status = 'NOT_BUILT'
            raise Exception('[Oftraf] Failure during building')

    def clean(self):
        """ Wrapper to the oftraf monitor build handler
        """
        oftraf_path = self.get_oftraf_path
        clean_hnd = oftraf_path + 'clean.sh'
        logging.info('[Oftraf] Cleaning')
        self.status = 'CLEANING'

        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([clean_hnd]),
                                         '[oftraf.clean_handler]')[0]
        if exit_status == 0:
            self.status = 'CLEANED'
            logging.info("[Oftraf] Successful cleaning")
        else:
            self.status = 'NOT CLEANED'
            raise Exception('[Oftraf] Failure during cleaning')

    def start(self):
        """ Wrapper to the oftraf monitor build handler
        """
        oftraf_path = self.get_oftraf_path
        start_hnd = oftraf_path + 'start.sh'
        logging.info('[Oftraf] Starting')
        self.status = 'STARTING'

        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([start_hnd]),
                                         '[oftraf.start_handler]')[0]
        if exit_status == 0:
            self.status = 'STARTED'
            logging.info("[Oftraf] Successful starting")
        else:
            self.status = 'NOT STARTED'
            raise Exception('[Oftraf] Failure during starting')

    def stop(self):
        """ Wrapper to the oftraf monitor build handler
        """
        oftraf_path = self.get_oftraf_path
        stop_hnd = oftraf_path + 'stop.sh'
        logging.info('[Oftraf] Starting')
        self.status = 'STOPPING'

        exit_status = \
            util.netutil.ssh_run_command(self._ssh_conn,
                                         ' '.join([stop_hnd]),
                                         '[oftraf.stop_handler]')[0]
        if exit_status == 0:
            self.status = 'STOPED'
            logging.info("[Oftraf] Successful stopping")
        else:
            self.status = 'NOT STOPPED'
            raise Exception('[Oftraf] Failure during stopping')

    def oftraf_get_of_counts(self):
        """Gets the openFlow packets counts, measured by oftraf
        """
        getheaders = {'Accept': 'application/json'}
        url = \
            'http://{0}:{1}/get_of_counts'.format(self.oftraf_rest_server.ip,
                                                  self.oftraf_rest_server.port)
        s = requests.Session()
        s.trust_env = False
        req = s.get(url, headers=getheaders, stream=False)
        return req.content.decode('utf-8')