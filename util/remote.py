# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Utilities for remote execution over SSH """

import paramiko
from multiprocessing import Queue

def remote_exec(cmd, transport, lines_queue=None):
    """
    Remotely executes a shell command over SSH.

    Executes the command and combines the stdout and stderr into a single
    output stream. The stream is dynamically splitted at newline boundaries and
    lines are posted into a queue for online processing. The combined output is
    returned as a string, and the command exit status is returned.

    :param cmd: shell command
    :param transport: SSH transport
    :param lines_queue: message queue to post stdout/stderr data
    :returns shell command exit status and shell command output
    :raises: paramiko.SSHException
    :rtype tuple(int,str)
    :type cmd: str
    :type transport: paramiko.Transport
    :type lines_queue: multiprocessing.Queue
    """

    chan = transport.open_session()
    chan.setblocking(1)
    chan.set_combine_stderr(True)
    chan.exec_command(cmd)
    cmdout = ''

    while True:
        out = chan.recv(8192).decode('UTF-8')
        if out == '':
            break
        cmdout += out
        if lines_queue is not None:
            for line in out.splitlines():
                lines_queue.put(line)

    return (chan.recv_exit_status(), cmdout)


if __name__ == '__main__':

    transport = paramiko.Transport(('127.0.0.1', 22))
    transport.connect(username='jenkins', password='jenkins')

    cmd = """echo "echo "This is on stdout"; echo "This is on stderr" >&2 ;
             echo "This is again on stdout"; exit 2" | bash"""

    queue = Queue()
    (status, out) = remote_exec(cmd, transport, queue)

    print('command exit status: ' + str(status))
    print('command output: [' + out + ']')

    print('')
    if not queue.empty():
        while True:
            print('queue item: <' + queue.get() + '>')
            if queue.empty():
                exit(0)
