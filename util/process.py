# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Process-related utilities """

import logging
import psutil
import subprocess


def get_pid_listening_on_port(port):
    """Finds if there is a running process listening for network connections
    on a specific port.
    :param port: the port number that we investigate.
    :return: -1, if no process is listening on port
    :return: 0, if some process is listening on port but we are not owner of it
    :return: <pid> of the process listening on port and we are owner of it
    """
    out = ''
    try:
        out = subprocess.check_output(
            'netstat -tulpn | grep \":' + str(port) + '\"', shell=True)
    finally:
        if out == '':
            return -1
        else:
            proc = out.split()[6]
            if proc == '-':  # process exists but we are not owner
                return 0
            else:
                return int(out.split()[6].split('/')[0])

def get_pid_listening_on_tcp_port(port):
    """Finds if there is a running process listening for network connections
    on a specific port.
    :param port: the port number that we investigate.
    :return: -1, if no process is listening on port
    :return: 0, if some process is listening on port but we are not owner of it
    :return: <pid> of the process listening on port and we are owner of it
    """
    out = ''
    try:
        logging.debug('Gonna find who is listening on port {0}'.format(port))
        out = subprocess.check_output(['fuser', str(port) + '/tcp'])
    finally:
        if out == '':
            return -1
        else:
            return int(out.strip())

def is_process_running(pid):
    """
    Finds if a process is running, using its process ID.
    :param pid: The process ID of the target process
    :return:  True, if the process is running
              False, otherwise
    """
    try:
        p = psutil.Process(pid)
        return p.is_running()
    except:
        return False
