# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" System statistics functions """

import psutil
import re
import subprocess

def sys_used_ram_mb():
    """ Return system used memory in MB """
    cmd = 'free -m | awk \'/^Mem:/{print $3}\''
    return int(subprocess.check_output(cmd, shell=True).strip())

def sys_free_ram_mb():
    """ Return system free memory in MB """
    cmd = 'free -m | awk \'/^Mem:/{print $4}\''
    return int(subprocess.check_output(cmd, shell=True).strip())

def sys_used_memory_bytes():
    """ Return system used memory in bytes """
    return psutil.virtual_memory().used

def sys_free_memory_bytes():
    """ Return system free memory in bytes """
    return psutil.virtual_memory().free

def sys_total_memory_bytes():
    """ Return system total memory in bytes """
    return psutil.virtual_memory().total

def sys_iowait_time():
    """
    For a given CPU, the I/O wait time is the time during which that CPU
    was idle (i.e. didn't execute any tasks) and there was at least one
    outstanding disk I/O operation requested by a task scheduled on that
    CPU (at the time it generated that I/O request).
    """
    return psutil.cpu_times().iowait

def proc_cmdline(pid):
    """ Returns the command line of a process as a list of strings
    :param pid: The proces ID of the target process"""
    cmd = psutil.Process(pid).cmdline
    if not isinstance(cmd, list):
        cmd = psutil.Process(pid).cmdline()
    return cmd

def proc_cwd(pid):
    """ Returns the process current working directory
    :param pid: The proces ID of the target process"""
    return psutil.Process(pid).getcwd()

def proc_cpu_affinity(pid):
    """  Returns the CPU affinity of a process as a list of processors
    :param pid: The proces ID of the target process"""
    return psutil.Process(pid).get_cpu_affinity()

def proc_cpu_system_time(pid):
    """ Returns the CPU system time of a process
    :param pid: The proces ID of the target process"""
    return psutil.Process(pid).get_cpu_times().system

def proc_cpu_user_time(pid):
    """ Returns the CPU user time of a process
    :param pid: The proces ID of the target process"""
    return psutil.Process(pid).get_cpu_times().user

def proc_vm_size(pid):
    """ Returns the virtual memory size of a process
    :param pid: The proces ID of the target process"""
    return psutil.Process(pid).get_memory_info().vms

def proc_num_fds(pid):
    """ Returns the number of file descriptors opened by this process
    :param pid: The proces ID of the target process"""
    return psutil.Process(pid).get_num_fds()

def proc_num_threads(pid):
    """ Returns the number of threads used by this process
    :param pid: The proces ID of the target process"""
    return psutil.Process(pid).get_num_threads()

def sys_load_average():
    """ Returns the system load average
    :returns: Tuple with the 1-,5- and 15-min load average
    """

    out = subprocess.check_output(['uptime'])
    m = re.search(r'load average: (.+), (.+), (.+)', out)
    return (m.group(1), m.group(2), m.group(3))
