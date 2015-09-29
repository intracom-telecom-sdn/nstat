# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Process-related utilities """

import logging
import subprocess
import sys
import time


def getpid_listeningonport(port):
    """Finds if there is a running process listening for network
    connections on a specific port.

    :param port: the port number that we investigate.
    :returns: -1, if no process is listening on port
               0, if some process is listening on port but we are not owner of
               it <pid> of the process listening on port and we are owner of it
    :rtype: int
    :type port: int
    """

    out = ''
    try:
        out = subprocess.check_output(
            'netstat -tulpn --numeric-ports | grep \":{0} \"'.format(port),
            shell=True, universal_newlines=True)
    finally:
        if out == '':
            return -1
        else:
            proc = out.split()[-1]
            # process exists but we are not owner
            if proc == '-':
                return 0
            else:
                return int(out.split()[-1].split('/')[0].strip())

def is_process_running(pid):
    """Finds if a process is running, using its process ID.

    :param pid: The process ID of the target process
    :returns: True, if the process is running False, otherwise
    :rtype: bool
    :type pid: int
    """

    out = '-1'
    try:
        cmd = 'kill -s 0 {0}'.format(pid)
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=True)
        out = p.stdout.read().decode(sys.stdout.encoding).strip()
    except subprocess.CalledProcessError as exc:
        out = exc.output
    finally:
        if out == '' or 'permitted' in out.split():
            return True
        else:
            return False

def wait_until_process_finishes(pid):
    """Waits until the process with the specified ID finishes

    :param pid: process id
    :type pid: int
    """

    while is_process_running(pid):
        time.sleep(1)
