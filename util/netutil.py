# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" General network utilities """

import logging
import os
import paramiko
import select
import socket
import stat
import time

def ssh_connect_or_return(ipaddr, user, passwd, maxretries, remote_port=22):
    """Opens a connection and returns a connection object. If it fails to open
    a connection after a specified number of tries, it returns -1.

    :param ipaddr: Ip adress of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param maxretries: maximum number of times to connect
    :returns: an ssh connection handle or -1 on failure
    :rtype: paramiko.SSHClient (or -1 when failure)
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type maxretries: int
    """

    retries = 1

    while retries <= maxretries:
        logging.info(
            '[netutil] Trying to connect to {0}:{1} ({2}/{3})'.
            format(ipaddr, remote_port, retries, maxretries))

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ipaddr, port=remote_port,
                        username=user, password=passwd)
            logging.info('[netutil] Connected to {0} '.format(ipaddr))
            return ssh
        except paramiko.AuthenticationException:
            logging.error(
                '[netutil] Authentication failed when connecting to {0}'.
                format(ipaddr))

        except:
            logging.error(
                '[netutil] Could not SSH to {0}, waiting for it to start'.
                format(ipaddr))

        retries += 1
        time.sleep(2)
    # If we exit while without ssh object been returned, then return -1
    logging.info('[netutil] Could not connect to {0}. Returning'
                 .format(ipaddr))
    return None


def ssh_copy_file_to_target(ipaddr, user, passwd, local_file, remote_file,
                            remote_port=22):
    """Copies local file on a remote machine target.

    :param ipaddr: Ip adress of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param local_file: file from local machine to copy,full location required
    :param remote_file: remote destination, full location required
    i.e /tmp/foo.txt
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type local_file: str
    :type remote_file: str
    :type remote_port: int
    """

    transport_layer = paramiko.Transport((ipaddr, remote_port))
    transport_layer.connect(username=user, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport_layer)
    sftp.put(local_file, remote_file)
    sftp.close()
    transport_layer.close()


def copy_directory_to_target(ipaddr, user, passwd, local_path, remote_path,
                             remote_port=22):
    """Copy a local directory on a remote machine.

    :param ipaddr: IP adress of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param local_path: directory path from local machine to copy, full location
    required
    :param remote_path: remote destination, full location required
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type local_path: str
    :type remote_path: str
    :type remote_port: int
    """

    #  recursively upload a full directory
    if local_path.endswith('/'):
        local_path = local_path[:-1]

    transport_layer = paramiko.Transport((ipaddr, remote_port))
    transport_layer.connect(username=user, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport_layer)
    os.chdir(os.path.split(local_path)[0])
    parent = os.path.split(local_path)[1]

    for walker in os.walk(parent):
        try:
            folder_to_make = os.path.join(remote_path, walker[0])
            sftp.mkdir(folder_to_make)
        except:
            pass
        for curr_file in walker[2]:
            local_file = os.path.join(walker[0], curr_file)
            remote_file = os.path.join(remote_path, walker[0], curr_file)
            sftp.put(local_file, remote_file)
    sftp.close()
    transport_layer.close()


def make_remote_file_executable(ipaddr, user, passwd, remote_file,
                                remote_port=22):
    """Makes the remote file executable.

    :param ipaddr: Ip adress of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param remote_file: remote file to make executable
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type remote_file: str
    :type remote_port: int
    """

    transport_layer = paramiko.Transport((ipaddr, remote_port))
    transport_layer.connect(username=user, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport_layer)
    sftp.chmod(remote_file, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
    sftp.close()
    transport_layer.close()


def create_remote_directory(ipaddr, user, passwd, remote_path, remote_port=22):
    """Opens an ssh connection to a remote machine and creates a new directory.

    :param ipaddr: Ip adress of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param remote_path: maximum number of times to connect
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type remote_path: str
    :type remote_port: int
    """

    transport_layer = paramiko.Transport((ipaddr, remote_port))
    transport_layer.connect(username=user, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport_layer)
    try:
        # Test if remote_path exists
        sftp.chdir(remote_path)
    except IOError:
        # Create remote_path
        sftp.mkdir(remote_path)
        sftp.chdir(remote_path)
    sftp.close()
    transport_layer.close()


def isdir(path, sftp):
    """Checks if a given remote path is a directory

    :param path: A string with the full path we want to check
    :param sftp: An sftp connection object (paramiko)
    :returns: True if the given path is a directory false otherwise.
    :rtype: bool
    :type path: str
    :type sftp: paramiko.SSHClient
    """

    try:
        return stat.S_ISDIR(sftp.stat(path).st_mode)
    except IOError:
        return False


def remove_remote_directory(ipaddr, user, passwd, path, remote_port=22):
    """Removes recursively remote directories (removes all files and
    other sub-directories).

    :param ipaddr: Ip adress of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param remote_file: remote file to make executable
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type remote_file: str
    :type remote_port: int
    """
    transport_layer = paramiko.Transport((ipaddr, remote_port))
    transport_layer.connect(username=user, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport_layer)

    files = sftp.listdir(path=path)

    for file_item in files:
        filepath = os.path.join(path, file_item)
        if isdir(filepath, sftp):
            remove_remote_directory(ipaddr, user, passwd, filepath)
        else:
            sftp.remove(filepath)

    sftp.rmdir(path)
    sftp.close()
    transport_layer.close()

# TODO - To be removed
def ssh_run_command_old(ssh_client, command_to_run):
    """Runs the specified command on a remote machine
    :param ssh_client : SSH client provided by paramiko to run the command
    :param command_to_run: Command to execute
    :returns: the output of the remotely executed command
    :rtype: tuple (stdin, stdout, stderr)
    :type ssh_client: paramiko.SSHClient
    :type command_to_run: str
    """

    return ssh_client.exec_command(command_to_run)


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
    :type ssh_client: paramiko.SSHClient
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
        return 0
    channel_output = ''
    while not channel.exit_status_ready():
        data = ''
        data = channel.recv(bufferSize).decode('utf-8')
        while data:
            channel_output += data
            if print_flag:
                logging.debug('{0} {1}'.format(prefix, data).rstrip())
            if lines_queue is not None:
                for line in data.splitlines():
                    lines_queue.put(line)
            data = channel.recv(bufferSize).decode('utf-8')

    channel_exit_status = channel.recv_exit_status()
    channel.close()
    return (channel_exit_status, channel_output)



def ssh_delete_file_if_exists(ipaddr, user, passwd, remote_file,
                              remote_port=22):
    """Deletes the file on e remote machine, if it exists

    :param ipaddr: Ip adress of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param remote_file: remote file to remove, full path must be used.
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type remote_file: str
    :type remote_port: int
    """
    transport_layer = paramiko.Transport((ipaddr, remote_port))
    transport_layer.connect(username=user, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport_layer)
    try:
        sftp.remove(remote_file)
        logging.info('[netutil] [delete_file_if_exists]: file {0} removed'.
                     format(remote_file))
    except IOError:
        logging.error(
            '[netutil] [delete_file_if_exists] IOError: The given remote_file '
            'is not valid. Error message: {0}'.format(IOError.strerror))
    except:
        logging.error(
            '[netutil] [delete_file_if_exists] Error: Unknown Error occured '
            'while was trying to remove remote file.')

    transport_layer.close()
    logging.error(
        '[netutil] [ssh_delete_file_if_exists]: transport layer closed')
