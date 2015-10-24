# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Module with functions for getting system and process statistics"""

import re
import subprocess
import sys
import util.netutil


def command_exec_wrapper(cmd, ssh_client=None):
    """Executes a command either locally or remotely and returns the result

    :param cmd: the command to be executed
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: The commands execution result as string
    :rtype: str
    :type cmd: str
    :type ssh_client: paramiko.SSHClient
    """

    if ssh_client is not None:
        cmd_status, cmd_output = util.netutil.ssh_run_command(ssh_client, cmd)
    else:
        cmd_output = str(subprocess.check_output(cmd, shell=True).
                         decode(sys.stdout.encoding))
    return cmd_output


def sys_used_ram_mb(ssh_client=None):
    """Returns system used memory in MB.

    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the amount of used RAM memory in the system in MB.
    :rtype: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = 'free -m | awk \'/^Mem:/{print $3}\''
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return int(cmd_output.strip())

def sys_nprocs(ssh_client=None):
    """Returns the number of CPUs in the system.

    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the number of CPUs in the system
    :rtype: int
    :type ssh_client: paramiko.SSHClient
    """
    cmd = 'cat /proc/cpuinfo | grep processor | wc -l'
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return int(cmd_output.strip())


def sys_free_ram_mb(ssh_client=None):
    """Returns system free memory in MB.

    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the amount of free RAM memory in the system in MB.
    :rtype: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = 'free -m | awk \'/^Mem:/{print $4}\''
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return int(cmd_output.strip())


def sys_used_memory_bytes(ssh_client=None):
    """Returns system used memory in bytes.

    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: The amount of used RAM memory in the system in bytes.
    :rtype: int
    :type ssh_client: paramiko.SSHClient
    """

    return sys_total_memory_bytes(ssh_client) - sys_free_memory_bytes(ssh_client)


def sys_free_memory_bytes(ssh_client=None):
    """Returns system free memory in bytes

    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the amount of free RAM memory in the system in bytes
    :rtype: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = 'cat /proc/meminfo | grep MemFree | awk \'{{print $2}}\''
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return int(cmd_output.strip())


def sys_total_memory_bytes(ssh_client=None):
    """Returns system total memory in bytes

    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: total system memory in bytes
    :rtype: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = 'cat /proc/meminfo | grep MemTotal | awk \'{{print $2}}\''
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return int(cmd_output.strip())


def sys_iowait_time(ssh_client=None):
    """For a given CPU, the I/O wait time is the time during which that CPU
    was idle (i.e. didn't execute any tasks) and there was at least one
    outstanding disk I/O operation requested by a task scheduled on that
    CPU (at the time it generated that I/O request).

    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the I/O wait time
    :rtype: float
    :type ssh_client: paramiko.SSHClient
    """

    cmd = 'cat /proc/stat | awk \'NR==1 {{print $6}}\''
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return float(cmd_output.strip())


def proc_cmdline(pid, ssh_client=None):
    """Returns the command line of a process as a string.

    :param pid: the process ID of the target process
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: The command execution output
    :rtype: str
    :type pid: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = "cat /proc/{0}/cmdline".format(pid)
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return cmd_output.strip().replace('\x00', '')


def proc_cwd(pid, ssh_client=None):
    """Method that returns the process current working directory.

    :param pid: the process ID of the target process
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the full path of working directory
    :rtype: str
    :type pid: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd1 = "cd /proc/{0}/cwd".format(pid)
    cmd2 = "pwd"
    command_exec_wrapper(cmd1, ssh_client)
    cmd_output = command_exec_wrapper(cmd2, ssh_client)
    return cmd_output.strip()


def proc_cpu_system_time(pid, ssh_client=None):
    """Method that returns the CPU system time of a process.

    :param pid: the process ID of the target process
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the CPU system time of a process
    :rtype: float
    :type pid: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = 'cat /proc/{0}/stat | awk \' {{ print $15 }} \''.format(pid)
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return float(cmd_output.strip())


def proc_cpu_user_time(pid, ssh_client=None):
    """Method that returns the CPU user time of a process.

    :param pid: the process ID of the target process
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the CPU user time of a process
    :rtype: float
    :type pid: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = 'cat /proc/{0}/stat | awk \'{{print $14}}\''.format(pid)
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return float(cmd_output.strip())


def proc_vm_size(pid, ssh_client=None):
    """Method that returns the virtual memory size of a process.

    :param pid: the process ID of the target process
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the virtual memory size of a process
    :rtype: int
    :type pid: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = ('cat /proc/{0}/status |grep VmSize | awk \'{{print $2}}\''.
           format(pid))
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return int(cmd_output.strip())*1024


def proc_num_fds(pid, ssh_client=None):
    """Returns the number of file descriptors opened by this process.

    :param pid: the process ID of the target process
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: total amount of open files for the specific process ID
    :rtype: int
    :type pid: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = 'ls -la /proc/{0}/fd | wc -l'.format(pid)
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return int(cmd_output.strip()) - 3


def proc_num_threads(pid, ssh_client=None):
    """Returns the number of threads used by this process.

    :param pid: the process ID of the target process
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the number of threads for the specific pid
    :rtype: int
    :type pid: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = ('cat /proc/{0}/status |grep Threads | awk \'{{print $2}}\''.
           format(pid))
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    return int(cmd_output.strip())


def sys_load_average(ssh_client=None):
    """Returns the system load average.

    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: tuple of floats with the 1-,5- and 15-min load average
    :rtype: tuple<float>
    :type ssh_client: paramiko.SSHClient
    """

    cmd = 'uptime'
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    matches = re.search(r'load average: (.+), (.+), (.+)', cmd_output.strip())
    return (float(matches.group(1)),
            float(matches.group(2)),
            float(matches.group(3)))

def get_java_options(pid, ssh_client=None):
    """Returns a list with all java options of a process defined by its
    process ID.

    :param pid: process id of the process we want to get the javaopts
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: a list with all java options
    :rtype: list<str>
    :type pid: int
    :type ssh_client: paramiko.SSHClient
    """

    cmd = 'ps -ef | grep \' {0} \''.format(pid)
    cmd_output = command_exec_wrapper(cmd, ssh_client)
    java_options = [o for o in cmd_output.strip().split() if o.startswith('-X')]
    return java_options

