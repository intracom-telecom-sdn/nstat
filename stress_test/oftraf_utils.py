# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
oftraf-related utilities
"""

import common
import json
import logging
import requests
import time

def oftraf_build(oftraf_build_handler, ssh_client=None):
    """Executes the oftraf build handler

    :param oftraf_build_handler: the full path to the build script of oftraf
    :param ssh_client: SSH client provided by paramiko to run the command
    :type oftraf_build_handler: str
    :type ssh_client: paramiko.SSHClient
    """

    common.command_exec_wrapper([oftraf_build_handler],
                                '[oftraf_build]',
                                ssh_client)


def oftraf_clean(oftraf_clean_handler, ssh_client=None):
    """Executes the oftraf clean handler

    :param oftraf_clean_handler: the full path to the clean script of oftraf
    :param ssh_client: SSH client provided by paramiko to run the command
    :type oftraf_clean_handler: str
    :type ssh_client: paramiko.SSHClient
    """

    common.command_exec_wrapper([oftraf_clean_handler], '[oftraf_clean]',
                                ssh_client)


def oftraf_start(oftraf_start_handler, controller_sb_interface,
                 oftraf_rest_port, ssh_client=None):
    """Executes the oftraf start handler

    :param oftraf_start_handler: the full path to the start script of oftraf
    :param controller_sb_interface: a named tuple python collection, containing
    controller IP address and controller openflow port
    :param oftraf_rest_port: the port number on which oftraf listens for REST
    calls
    :param ssh_client: SSH client provided by paramiko to run the command
    :type oftraf_start_handler: str
    :type controller_sb_interface: collections.namedtuple<str,int>
    :type oftraf_rest_port: int
    :type ssh_client: paramiko.SSHClient
    """

    common.command_exec_wrapper(
        [oftraf_start_handler, controller_sb_interface.ip,
         controller_sb_interface.port, str(oftraf_rest_port)], '[oftraf_start]',
        ssh_client)


def oftraf_stop(oftraf_stop_handler, oftraf_rest_server, ssh_client=None):
    """Executes the oftraf stop handler

    :param oftraf_stop_handler: the full path to the stop script of oftraf
    :param oftraf_rest_port: the port number on which oftraf listens for REST
    calls
    :param ssh_client: SSH client provided by paramiko to run the command
    :type oftraf_start_handler: str
    :type oftraf_rest_port: int
    :type ssh_client: paramiko.SSHClient
    """

    common.command_exec_wrapper(
        [oftraf_stop_handler, oftraf_rest_server.ip,
         str(oftraf_rest_server.port)], '[oftraf_clean]', ssh_client)


def oftraf_get_throughput(oftraf_rest_server):
    """Gets the Throughput value measured by oftraf

    :param oftraf_rest_server: a named tuple python collection, containing the
    IP address and the port number of oftraf rest server
    :type oftraf_rest_server: collections.namedtuple<str,int>
    """

    getheaders = {'Accept': 'application/json'}
    url = 'http://{0}:{1}/get_of_counts'.format(oftraf_rest_server.ip,
                                                oftraf_rest_server.port)
    s = requests.Session()
    req = s.get(url, headers=getheaders, stream=False)
    return req.content.decode('utf-8')


def oftraf_monitor_thread(oftraf_interval_ms, oftraf_rest_server,
                          results_queue):
    """Function executed inside a thread and returns the output throughput,
    measured by oftraf

    :param oftraf_interval_ms: interval in milliseconds, after which we want
    to get an oftraf measurement
    :param oftraf_rest_server: a named tuple python collection, containing the
    IP address and the port number of oftraf rest server
    :param results_queue: the multiprocessing Queue used for the communication
    between the NSATA master thread and oftraf thread. In this Queue we return
    the result
    :type oftraf_interval_ms: int
    :type oftraf_rest_server: collections.namedtuple<str,int>
    :type results_queue: multiprocessing.Queue
    """

    oftraf_interval_sec = oftraf_interval_ms / 1000
    logging.info('[oftraf_monitor_thread] Waiting for {0} seconds.'.
                 format(oftraf_interval_sec))
    time.sleep(oftraf_interval_sec)
    logging.info('[oftraf_monitor_thread] get throughput of controller')
    throughput_response = json.loads(oftraf_get_throughput(oftraf_rest_server))
    out_traffic = tuple(throughput_response['OF_out_counts'])
    results_queue.put(out_traffic)

