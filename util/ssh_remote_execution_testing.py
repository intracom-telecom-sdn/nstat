import logging
import os
import paramiko
import socket
import stat
import time

import queue

def ssh_run_command(ssh_client, command_to_run, prefix='', lines_queue=None,
                    print_flag=True, block_flag=True):
    """Runs the specified command on a remote machine

    :param ssh_client : SSH client provided by paramiko to run the command
    :param command_to_run: Command to execute
    :param lines_queue: Queue datastructure to buffer the result of execution
    :param print_flag: Flag that defines if the output of the command will be
    printed on screen
    :param block_flag: Defines if we block execution waiting for the running
    command to return its exit status
    :returns: the exit code of the command to be executed remotely and the
    combined stdout - stderr of the executed command
    :rtype: tuple<int, str>
    :type ssh_session: paramiko.SSHClient
    :type command_to_run: str
    :type lines_queue: queue<str>
    :type print_flag: bool
    :type block_flag: bool
    :exception SSHException: Raised when fails to open a channel from
    ssh_client object
    :exception UnicodeDecodeError: Raised when it fails to decode received
    data into UTF-8
    :exception socket.timeout: When the channel remains idle for a timeout
    period (in sec) defined in implementation of the function
    """

    channel = ssh_client.get_transport().open_session()
    bufferSize = 4*1024
    channel_timeout = 300 
    channel.setblocking(1)
    channel.set_combine_stderr(True)
    channel.settimeout(channel_timeout)
    channel.exec_command(command_to_run)
    if not block_flag:
        return
    channel_output = ''
    while not channel.exit_status_ready():
        data = ''
        data = channel.recv(bufferSize).decode('utf-8')
        while data:
            channel_output += data
            if print_flag:
                print('{0} {1}'.format(prefix, data))
            if lines_queue is not None:
                for line in data.splitlines():
                    lines_queue.put(line)
            data = channel.recv(bufferSize).decode('utf-8')

    channel_exit_status = channel.recv_exit_status()
    channel.close()
    return (channel_exit_status, channel_output)

if __name__ == '__main__':
    S = "this is string example....wow!!!"
    S = S.encode('ASCII','strict')

    print("Encoded String: " + str(S))
    print("Decoded String: " + S.decode('utf-8'))
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='127.0.0.1', port=22,
                        username='jenkins', password='jenkins')
    cmd = 'ls -la'
    exit_status, output = ssh_run_command(ssh_client, cmd, '[Functional_test] ', None, True)
    print('PRINTING RETURNED OUTPUT: \n'+output)

    cmd = '''echo "This is on stderr" >&2 '''
    ssh_run_command(ssh_client, cmd, '[Functional_test] ', None, True)

    cmd = 'echo $HOME'
    ssh_run_command(ssh_client, cmd, '[Functional_test] ', None, True)

    cmd = 'exit 2'
    print('ERROR NUMBER RETURNED: {0}'.format(ssh_run_command(ssh_client, cmd)))

    testing_queue = queue.Queue()
    cmd = 'ls -1'
    print('   === USING QUEUE to buffer results')
    ssh_run_command(ssh_client, cmd, '[Functional_test] ', testing_queue, False)
    print('   === Printing queue buffered results after execution:')
    while not testing_queue.empty():
        print(testing_queue.get())
    print('  === RUNNING COMMAND IN NON BLOCKING MODE:')
    ssh_run_command(ssh_client, cmd, '[Functional_test] ', testing_queue, False, False)