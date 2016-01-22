# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
oftraf-related utilities
"""

import common
import requests

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

    common.command_exec_wrapper([oftraf_clean_handler],
                                '[oftraf_clean]',
                                ssh_client)


def oftraf_start(oftraf_start_handler, controller_ip, controller_of_port,
                 oftraf_rest_port, ssh_client=None):
    """Executes the oftraf start handler

    :param oftraf_start_handler: the full path to the start script of oftraf
    :param controller_ip: the ip address of the controller
    :param controller_of_port: the port number on which the controller listens
    for openflow connections
    :param oftraf_rest_port: the port number on which oftraf listens for REST
    calls
    :param ssh_client: SSH client provided by paramiko to run the command
    :type oftraf_start_handler: str
    :type controller_ip: str
    :type controller_of_port: int
    :type oftraf_rest_port: int
    :type ssh_client: paramiko.SSHClient
    """

    common.command_exec_wrapper(
        [oftraf_start_handler, controller_ip, controller_of_port,
         oftraf_rest_port], '[oftraf_start]', ssh_client)


def oftraf_stop(oftraf_stop_handler, oftraf_rest_port, ssh_client=None):
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
        [oftraf_stop_handler, oftraf_rest_port], '[oftraf_clean]', ssh_client)


def oftraf_get_throughput(oftraf_rest_ip, oftraf_rest_port):
    """Gets the Throughput value measured by oftraf

    :param oftraf_rest_ip: the IP address where oftraf REST server runs
    :param oftraf_rest_port: the port number where oftraf listens for REST
    requests
    :type oftraf_rest_ip: str
    :type oftraf_rest_port: int
    """

    getheaders = {'Accept': 'application/json'}
    url = 'http://{0}:{1}/get_of_counts'.format(oftraf_rest_ip,
                                                oftraf_rest_port)
    s = requests.Session()
    req = s.get(url, headers=getheaders, stream=False)
    return req.content.decode('utf-8')
