# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Module with functions for getting system and process statistics"""

import re
import subprocess
import sys


def sys_used_ram_mb():
    """Returns system used memory in MB.

    :returns: the amount of used RAM memory in the system in MB.
    :rtype: int
    """

    cmd = 'free -m | awk \'/^Mem:/{print $3}\''
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return int(out)

def sys_nprocs():
    """Returns the number of CPUs in the system.

    :returns: the number of CPUs in the system
    :rtype: int
    """
    cmd = 'cat /proc/cpuinfo | grep processor | wc -l'
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return int(out)


def sys_free_ram_mb():
    """Returns system free memory in MB.

    :returns: the amount of free RAM memory in the system in MB.
    :rtype: int
    """

    cmd = 'free -m | awk \'/^Mem:/{print $4}\''
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return int(out)


def sys_used_memory_bytes():
    """Returns system used memory in bytes.

    :returns: The amount of used RAM memory in the system in bytes.
    :rtype: int
    """

    return sys_total_memory_bytes() - sys_free_memory_bytes()


def sys_free_memory_bytes():
    """Returns system free memory in bytes

    :returns: the amount of free RAM memory in the system in bytes
    :rtype: int
    """
    cmd = 'cat /proc/meminfo | grep MemFree | awk \'{{print $2}}\''
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return int(out)


def sys_total_memory_bytes():
    """Returns system total memory in bytes

    :returns: total system memory in bytes
    :rtype: int
    """

    cmd = 'cat /proc/meminfo | grep MemTotal | awk \'{{print $2}}\''
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return int(out)


def sys_iowait_time():
    """For a given CPU, the I/O wait time is the time during which that CPU
    was idle (i.e. didn't execute any tasks) and there was at least one
    outstanding disk I/O operation requested by a task scheduled on that
    CPU (at the time it generated that I/O request).

    :returns: the I/O wait time
    :rtype: float
    """

    cmd = 'cat /proc/stat | awk \'NR==1 {{print $6}}\''
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return float(out)


def proc_cmdline(pid):
    """Returns the command line of a process as a string.

    :param pid: the process ID of the target process
    :returns: The command execution output
    :rtype: str
    :type pid: int
    """

    cmd = "cat /proc/{0}/cmdline".format(pid)
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return out


def proc_cwd(pid):
    """Method that returns the process current working directory.

    :param pid: the process ID of the target process
    :returns: the full path of working directory
    :rtype: str
    :type pid: int
    """

    cmd1 = "cd /proc/{0}/cwd".format(pid)
    cmd2 = "pwd"

    subprocess.check_output(cmd1, shell=True)
    out = str(subprocess.check_output(cmd2, shell=True).
              decode(sys.stdout.encoding)).strip()
    return out



def proc_cpu_system_time(pid):
    """Method that returns the CPU system time of a process.

    :param pid: the process ID of the target process
    :returns: the CPU system time of a process
    :rtype: float
    :type pid: int
    """

    cmd = 'cat /proc/{0}/stat | awk \' {{ print $15 }} \''.format(pid)
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return float(out)


def proc_cpu_user_time(pid):
    """Method that returns the CPU user time of a process.

    :param pid: the process ID of the target process
    :returns: the CPU user time of a process
    :rtype: float
    :type pid: int
    """

    cmd = 'cat /proc/{0}/stat | awk \'{{print $14}}\''.format(pid)
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return float(out)


def proc_vm_size(pid):
    """Method that returns the virtual memory size of a process.

    :param pid: the process ID of the target process
    :returns: the virtual memory size of a process
    :rtype: int
    :type pid: int
    """

    cmd = ('cat /proc/{0}/status |grep VmSize | awk \'{{print $2}}\''.
           format(pid))
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return int(out)*1024


def proc_num_fds(pid):
    """Returns the number of file descriptors opened by this process.

    :param pid: the process ID of the target process
    :returns: total amount of open files for the specific process ID
    :rtype: int
    :type pid: int
    """

    cmd = 'ls -la /proc/{0}/fd | wc -l'.format(pid)
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return int(out) - 3


def proc_num_threads(pid):
    """Returns the number of threads used by this process.

    :param pid: the process ID of the target process
    :returns: the number of threads for the specific pid
    :rtype: int
    :type pid: int
    """

    cmd = ('cat /proc/{0}/status |grep Threads | awk \'{{print $2}}\''.
           format(pid))

    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    return int(out)


def sys_load_average():
    """Returns the system load average.

    :returns: tuple of floats with the 1-,5- and 15-min load average
    :rtype: tuple<float>
    """

    cmd = 'uptime'
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    matches = re.search(r'load average: (.+), (.+), (.+)', out)
    return (float(matches.group(1)),
            float(matches.group(2)),
            float(matches.group(3)))

def get_java_options(pid):
    """Returns a list with all java options of a process defined by its
    process ID.

    :param pid: process id of the process we want to get the javaopts
    :returns: a list with all java options
    :rtype: list<str>
    :type pid: int
    """

    cmd = 'ps -ef | grep \' {0} \''.format(pid)
    out = str(subprocess.check_output(cmd, shell=True).
              decode(sys.stdout.encoding)).strip()
    java_options = [o for o in out.split() if o.startswith('-X')]
    return java_options

