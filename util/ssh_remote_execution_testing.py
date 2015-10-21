import logging
import os
import paramiko
import socket
import stat
import sys
import time

import queue

def ssh_run_command(ssh_client, command_to_run, lines_queue=None):
    """Runs the specified command on a remote machine

    :param ssh_client : SSH client provided by paramiko to run the command
    :param command_to_run: Command to execute
    :param lines_queue: Queue datastructure to buffer the result of execution
    :returns: the exit code of the command to be executed remotely
    :rtype: int
    :type ssh_session: paramiko.SSHClient
    :type command_to_run: str
    :type lines_queue: <queue>
    """

    channel = ssh_client.get_transport().open_session()
    bufferSize = 4*1024
    # We currently do not use channel_timeout
    channel_timeout = 300 
    channel.setblocking(1)
    channel.set_combine_stderr(True)
    #channel.settimeout(channel_timeout)
    channel.exec_command(command_to_run)
    while not channel.exit_status_ready():
        try:
            data = ''
            if channel.recv_ready():
                data = channel.recv(bufferSize).decode(sys.stdout.encoding).strip()
                while data:
                    if lines_queue == None:
                        print(data)
                    else:
                        for line in data.splitlines():
                            lines_queue.put(line)
                    data = channel.recv(bufferSize).decode(sys.stdout.encoding).strip()

        except  socket.timeout:
            # Replace print with logging.error
            print('  ===ERROR=== Socket timeout exception caught')
            break
        except Exception:
            # Replace print with logging.error
            print('  ===ERROR=== General exception caught')
            break
    
    channel_exit_status = channel.recv_exit_status()
    channel.close()
    if channel_exit_status is not None:
        return channel.recv_exit_status()
    else:
        return 1

if __name__ == '__main__':

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='127.0.0.1', port=22,
                        username='jenkins', password='jenkins')
    cmd = 'ls -la'
    ssh_run_command(ssh_client, cmd)

    cmd = '''echo "This is on stderr" >&2 '''
    ssh_run_command(ssh_client, cmd)

    cmd = 'echo $HOME'
    ssh_run_command(ssh_client, cmd)

    cmd = 'exit 2'
    print('ERROR NUMBER RETURNED: {0}'.format(ssh_run_command(ssh_client, cmd)))

    testing_queue = queue.Queue()
    cmd = 'ls -1'
    print('   === USING QUEUE to buffer results')
    ssh_run_command(ssh_client, cmd, testing_queue)
    print('   === Printing queue buffered results after execution:')
    while not testing_queue.empty():
        print(testing_queue.get())