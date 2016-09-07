# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" General network utilities """

import logging
import os
import paramiko
import stat
import time

def copy_dir_local_to_remote(connection, local_path, remote_path):
    """Copy a local directory on a remote machine.

    :param connection: A named tuple with all the connection information.
    It must have the following elements:
    ['name', 'ip', 'ssh_port', 'username', 'password']
    :param local_path: directory path from local machine to be copied, full
    location required
    :param remote_path: directory path on the remote node, full location
    required
    :type connection: namedtuple<>
    :type local_path: str
    :type remote_path: str
    """

    if local_path.endswith('/'):
        local_path = local_path[:-1]
    (sftp, transport_layer) = ssh_connection_open(connection)
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

    ssh_connection_close(sftp, transport_layer)

def copy_dir_remote_to_local(connection, remote_path, local_path):
    """Copy recursively remote directories (Copies all files and other
    sub-directories).

    :param connection: named tuple with connection information: ['name', 'ip',
    'ssh_port', 'username', 'password']
    :param remote_path: full remote path we want to copy
    :param local_path: full local path we want to copy
    :type connection: namedtuple<>
    :type remote_path: str
    :type local_path: str
    """
    (sftp, transport_layer) = ssh_connection_open(connection)
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    files = sftp.listdir(path=remote_path)

    for file_item in files:
        if file_item != None:
            remote_filepath = os.path.join(remote_path, file_item)
            if isdir(remote_filepath, sftp):
                if not os.path.exists(os.path.join(local_path, file_item)):
                    os.makedirs(os.path.join(local_path, file_item))
                copy_dir_remote_to_local(connection, remote_filepath,
                                      os.path.join(local_path, file_item))
            else:
                sftp.get(remote_filepath, os.path.join(local_path, file_item))
    ssh_connection_close(sftp, transport_layer)

def create_dir_remote(connection, remote_path):
    """Opens an ssh connection to a remote machine and creates a new directory.

    :param connection: named tuple with connection information: ['name', 'ip',
    'ssh_port', 'username', 'password']
    :param remote_path:
    :type connection: namedtuple<>
    :type remote_path: str
    """

    (sftp, transport_layer) = ssh_connection_open(connection)
    try:
        # Test if remote_path exists
        sftp.chdir(remote_path)
    except IOError:
        # Create remote_path
        sftp.mkdir(remote_path)
        sftp.chdir(remote_path)
    ssh_connection_close(sftp, transport_layer)


def isdir(path, sftp):
    """Checks if a given remote path is a directory

    :param path: A string with the full path we want to check
    :param sftp: An sftp connection object (paramiko)
    :returns: True if the given path is a directory false otherwise.
    :rtype: bool
    :type path: str
    :type sftp: paramiko.SFTPClient
    """

    try:
        return stat.S_ISDIR(sftp.stat(path).st_mode)
    except IOError:
        return False

def remote_file_exists(path, filename, ssh):
    """Checks if a given remote file exists
    :param path: A string with the full path where the file to be checked has be placed
    :param filename: A file under the param path we want to check
    :param ssh: An sftp connection object (paramiko)
    :returns: True if the given path is a directory false otherwise.
    :rtype: bool
    :type path: str
    :type filename: str 
    :type ssh: paramiko.SFTPClient
    """

    try:
        sftp = ssh.open_sftp()
        sftp.chdir(path)
        sftp.stat(filename)

    except IOError:
        return False

def check_remote_file(path_file, ssh, pattern):
    """Checks if a given pattern exist within a remote file
    :param path_file: A string with the full path and the file anme to be opened
    :param ssh: An sftp connection object (paramiko)
    :param pattern: the tezt to be checked if exists in the file 
    :returns: True if the given path is a directory false otherwise.
    :rtype: bool
    :type path_file: str
    :type ssh: paramiko.SFTPClient
    :type pattern: str 
    """
    try:  
        sftp_client = ssh.open_sftp()
        remote_file = sftp_client.open(path_file)

        for line in remote_file:
            if pattern in line:
                return True
            else:
                continue
            return False
    except IOError:
        print ('ERROR')
        return False


def make_remote_file_executable(connection, remote_file):
    """Makes the remote file executable.

    :param connection: named tuple with connection information: ['name', 'ip',
    'ssh_port', 'username', 'password']
    :param remote_file: remote file to make executable
    :type connection: namedtuple<>
    :type remote_file: str
    """
    (sftp, transport_layer) = ssh_connection_open(connection)
    sftp.chmod(remote_file, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
    ssh_connection_close(sftp, transport_layer)

def remove_remote_directory(connection, path):
    """Removes recursively remote directories (removes all files and
    other sub-directories).

    :param connection: named tuple with connection information: ['name', 'ip',
    'ssh_port', 'username', 'password']
    :param path: A string with the full path we want to remove
    :type connection: namedtuple<>
    :type path: str
    """

    (sftp, transport_layer) = ssh_connection_open(connection)
    files = sftp.listdir(path=path)

    for file_item in files:
        filepath = os.path.join(path, file_item)
        if isdir(filepath, sftp):
            remove_remote_directory(connection, filepath)
        else:
            sftp.remove(filepath)

    sftp.rmdir(path)
    ssh_connection_close(sftp, transport_layer)

def ssh_connect_or_return(connection, maxretries):
    """Opens a connection and returns a connection object. If it fails to open
    a connection after a specified number of tries, it returns -1.

    :param connection: named tuple with connection information: ['name', 'ip',
    'ssh_port', 'username', 'password']
    :param maxretries: maximum number of times to connect
    :returns: an ssh connection handle or -1 on failure
    :rtype: paramiko.SSHClient (or -1 when failure)
    :type connection: namedtuple<>
    :type maxretries: int
    """

    retries = 1

    while retries <= maxretries:
        logging.info(
            '[ssh_connect_or_return] Trying to connect to {0}:{1} ({2}/{3})'.
            format(connection.ip, connection.ssh_port, retries, maxretries))

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=connection.ip, port=connection.ssh_port,
                        username=connection.username,
                        password=connection.password)
            logging.info('[ssh_connect_or_return] connected to {0} '.
                         format(connection.ip))
            return ssh
        except paramiko.AuthenticationException:
            logging.error(
                '[ssh_connect_or_return] authentication failed when connecting to {0}'.
                format(connection.ip))

        retries += 1
        time.sleep(2)
    # If we exit while without ssh object been returned, then return -1
    raise Exception('[netutil] could not connect to {0}. Returning'
                 .format(connection.ip))



def ssh_connect_or_return2(ip, ssh_port, username, password, maxretries):
    """Opens a connection and returns a connection object. If it fails to open
    a connection after a specified number of tries, it returns -1.

    :param ip: controller IP address
    :param ssh_port: controller port
    :param username: username of the remote user
    :param password: password of the remote user
    :param maxretries: maximum number of times to connect
    :returns: an ssh connection handle or -1 on failure
    :rtype: paramiko.SSHClient (or -1 when failure)
    :type ip: str
    :type ssh_port: int
    :type username: str
    :type password: str
    :type maxretries: int
    """

    retries = 1

    while retries <= maxretries:
        logging.info(
            '[ssh_connect_or_return] Trying to connect to {0}:{1} ({2}/{3})'.
            format(ip, ssh_port, retries, maxretries))

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.load_host_keys(os.path.expanduser(os.path.join("~",".ssh","known_hosts")))
            ssh.connect(hostname=ip, port=ssh_port,
                        username=username,
                        password=password)
            logging.info('[ssh_connect_or_return] connected to {0} '.
                         format(ip))
            return ssh
        except paramiko.AuthenticationException:
            logging.error(
                '[ssh_connect_or_return] authentication failed when connecting to {0}'.
                format(ip))

        retries += 1
        time.sleep(2)
    # If we exit while without ssh object been returned, then return -1
    raise Exception('[netutil] could not connect to {0}. Returning'
                 .format(ip))

def ssh_connection_close(sftp, transport_layer):
    """ Closes an ssh connection with a remote node

    :param sftp:
    :param transport_layer:
    :type sftp: paramiko.SFTPClient
    :type transport_layer: paramiko.Transport
    """
    try:
        sftp.close()
        transport_layer.close()
    except:
        pass


def ssh_connection_open(connection):
    """ Opens an ssh connection on a remote node

    :param connection: named tuple with connection information: ['name', 'ip',
    'ssh_port', 'username', 'password']
    :returns sftp, transport_layer
    :rtype tuple<paramiko.SFTPClient, paramiko.Transport>
    :type connection: collections.namedtuple
    """
    try:
        transport_layer = paramiko.Transport((connection.ip, connection.ssh_port))
        transport_layer.connect(username=connection.username,
                                password=connection.password)
        sftp = paramiko.SFTPClient.from_transport(transport_layer)

        return (sftp, transport_layer)
    except:
        logging.error('[ssh_connection_open] error: check connection object')


def ssh_copy_file_to_target(connection, local_file, remote_file):
    """Copies local file on a remote machine target.

    :param connection: named tuple with connection information: ['name', 'ip',
    'ssh_port', 'username', 'password']
    :param local_file: file from local machine to copy,full location required
    :param remote_file: remote destination, full location required
    i.e /tmp/foo.txt
    :type connection: collections.namedtuple
    :type local_file: str
    :type remote_file: str
    """
    (sftp, transport_layer) = ssh_connection_open(connection)
    sftp.put(local_file, remote_file)
    ssh_connection_close(sftp, transport_layer)


def ssh_delete_file_if_exists(connection, remote_file):
    """Deletes the file on a remote machine, if exists

    :param connection: named tuple with connection information: ['name', 'ip',
    'ssh_port', 'username', 'password']
    :param remote_file: remote file to remove, full path must be used.
    :type connection: collections.namedtuple
    :type remote_file: str
    """

    (sftp, transport_layer) = ssh_connection_open(connection)
    try:
        sftp.remove(remote_file)
        logging.info('[delete_file_if_exists]: file {0} removed'.
                     format(remote_file))
    except IOError:
        logging.error(
            '[delete_file_if_exists] IOError: The given remote_file '
            'is not valid. Error message: {0}'.format(IOError.strerror))
    except:
        logging.error(
            '[delete_file_if_exists] Error: unknown error occurred '
            'removing remote file.')

    ssh_connection_close(sftp, transport_layer)


def ssh_run_command(ssh_client, command_to_run, prefix='', lines_queue=None,
                    print_flag=True, block_flag=True, getpty_flag=False):
    """Runs the specified command on a remote machine

    :param ssh_client : SSH client provided by paramiko to run the command
    :param command_to_run: Command to execute
    :param prefix: prefix of log message
    :param lines_queue: Queue datastructure to buffer the result of execution
    :param print_flag: Flag that defines if the output of the command will be
    printed on screen
    :param block_flag: Defines if we block execution waiting for the running
    command to return its exit status
    :param getpty_flag: add a pseudo-terminal console (pty console) to the
    channel
    :returns: the exit code of the command to be executed remotely and the
    combined stdout - stderr of the executed command
    :rtype: tuple<int, str>
    :type ssh_client: paramiko.SSHClient
    :type command_to_run: str
    :type prefix: str
    :type lines_queue: queue<str>
    :type print_flag: bool
    :type block_flag: bool
    :type getpty_flag: bool
    """

    channel = ssh_client.get_transport().open_session()
    bufferSize = 4*1024
    channel_timeout = None
    channel.setblocking(1)
    channel.set_combine_stderr(True)
    channel.settimeout(channel_timeout)
    if getpty_flag:
        channel.get_pty()
    channel.exec_command(command_to_run)

    if not block_flag:
        return 0

    channel_output = ''
    while not channel.exit_status_ready():
        data = ''
        data = channel.recv(bufferSize).decode('utf-8')
        while data is not '':
            channel_output += data
            if print_flag:
                logging.debug('{0} {1}'.format(prefix, data).strip())
            if lines_queue is not None:
                for line in data.splitlines():
                    lines_queue.put(line)
            data = channel.recv(bufferSize).decode('utf-8')

    channel_exit_status = channel.recv_exit_status()
    channel.close()
    return (channel_exit_status, channel_output)
