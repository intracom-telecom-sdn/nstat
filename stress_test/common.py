# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Reusable functions for stress tests """

import logging
import requests
import subprocess
import time
import util.file_ops
import util.process
import util.sysstats


def check_ds_switches(controller_ip, controller_restconf_port, auth_token):
    """Query number of switches registered in ODL operational DS

    :param controller_ip: controller IP address
    :param controller_restconf_port: controller restconf port
    :param auth_token: tuple with controller restconf user and password
    (controller_restconf_user, controller_restconf_password)
    :returns: number of switches found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    :type controller_ip: str
    :type controller_restconf_port: int
    :type auth_token: tuple<str>
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(controller_ip, controller_restconf_port))

    try:
        datastore = requests.get(url=url,
            auth=auth_token).json()['topology'][0]
    except:
        return -1

    switches = [node for node in datastore.get('node', []) if not node['node-id'].startswith('host:')]
    return len(switches)


def check_ds_hosts(controller_ip, controller_restconf_port, auth_token):
    """Query number of hosts registered in ODL operational DS

    :param controller_ip: controller IP address
    :param controller_restconf_port: controller restconf port
    :param auth_token: tuple with controller restconf user and password
    (controller_restconf_user, controller_restconf_password)
    :returns: number of hosts found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    :type controller_ip: str
    :type controller_restconf_port: int
    :type auth_token: tuple<str>
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(controller_ip, controller_restconf_port))

    try:
        datastore = requests.get(url=url,
            auth=auth_token).json()['topology'][0]
    except:
        return -1

    hosts = [node for node in datastore.get('node', []) if node['node-id'].startswith('host:')]
    return len(hosts)


def check_ds_links(controller_ip, controller_restconf_port, auth_token):
    """Query number of links registered in ODL operational DS

    :param controller_ip: controller IP address
    :param controller_restconf_port: controller restconf port
    :param auth_token: tuple with controller restconf user and password
    (controller_restconf_user, controller_restconf_password)
    :returns: number of links found, 0 if none exists and -1 in case of error.
    :rtype: int
    :type controller_ip: str
    :type controller_restconf_port: int
    :type auth_token: tuple<str>
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(controller_ip, controller_restconf_port))

    try:
        datastore = requests.get(url=url,
            auth=auth_token).json()['topology'][0]
    except:
        return -1

    links = [link for link in datastore.get('link', [])]
    return len(links)


def poll_ds_thread(controller_ip, controller_restconf_port,
                   controller_restconf_user, controller_restconf_password,
                   boot_start_time, bootup_time_ms,
                   cbench_thread_creation_delay_ms, expected_switches,
                   discovery_deadline_ms, queuecomm):
    """
    Poll operational DS to discover installed switches

    :param controller_ip: controller IP address
    :param controller_restconf_port: controller restconf port
    :param auth_token: tuple with controller restconf user and controller
    restconf password (controller_restconf_user, controller_restconf_password)
    :param boot_start_time: The time we begin starting topology switches
    :param bootup_time_ms: Time to bootup switches topology (in ms). We start
    discovery process after this time.
    :param cbench_thread_creation_delay_ms: Delay before the creation of a
    cbench thread (in ms)
    :param expected_switches: switches expected to find in the DS
    :param discovery_deadline_ms: deadline (in ms) at which the thread
    should discover switches (in milliseconds)
    :param queuecomm: queue for communicating with the main context
    :type controller_ip: str
    :type controller_restconf_port: int
    :type controller_restconf_auth_token: tuple<str>
    :type boot_start_time: int
    :type bootup_time_ms: int
    :type cbench_thread_creation_delay_ms: int
    :type expected_switches: int
    :type discovery_deadline_ms: float
    :type queuecomm: multiprocessing.Queue
    """

    discovery_deadline = float(discovery_deadline_ms.value) / 1000
    sleep_before_discovery = float(bootup_time_ms.value) / 1000
    cbench_thread_creation_delay = float(cbench_thread_creation_delay_ms) / 1000
    logging.info('[poll_ds_thread] Monitor thread started')
    t_start = boot_start_time.value
    time.sleep(sleep_before_discovery)
    logging.info('[poll_ds_thread] Starting discovery')
    t_discovery_start = time.time()
    discovered_switches = 0

    while True:

        if (time.time() - t_discovery_start) > discovery_deadline:
            logging.info(
                '[poll_ds_thread] Deadline of {0} seconds passed, discovered '
                '{1} switches.'.format(discovery_deadline,
                                       discovered_switches))

            queuecomm.put((-1.0, discovered_switches))
            return
        else:
            discovered_switches = check_ds_switches(controller_ip.value.decode(),
                controller_restconf_port.value,
                (controller_restconf_user.value.decode(),
                 controller_restconf_password.value.decode()))

            if discovered_switches == expected_switches.value:
                delta_t = time.time() - t_start - cbench_thread_creation_delay
                logging.info(
                    '[poll_ds_thread] {0} switches found in {1} seconds'.
                    format(discovered_switches, delta_t))

                queuecomm.put((delta_t, discovered_switches))
                return
        time.sleep(1)


def sample_stats(cpid, ssh_client=None):
    """ Take runtime statistics

    :param cpid: controller PID
    :param ssh_client : SSH client provided by paramiko to run the command
    :returns: the statistics in a dictionary
    :rtype: dict
    :type cpid: int
    :type ssh_client: paramiko.SSHClient
    """

    common_statistics = {}
    common_statistics['total_memory_bytes'] = \
        util.sysstats.sys_total_memory_bytes(ssh_client)
    common_statistics['controller_cwd'] = util.sysstats.proc_cwd(cpid, ssh_client)
    common_statistics['controller_java_xopts'] = \
        util.sysstats.get_java_options(cpid, ssh_client)
    common_statistics['timestamp'] = \
        int(subprocess.check_output('date +%s', shell=True,
                                              universal_newlines=True).strip())
    common_statistics['date'] = subprocess.check_output('date', shell=True,
                                     universal_newlines=True).strip()
    common_statistics['used_memory_bytes'] = \
        util.sysstats.sys_used_memory_bytes(ssh_client)
    common_statistics['free_memory_bytes'] = \
        util.sysstats.sys_free_memory_bytes(ssh_client)
    common_statistics['controller_cpu_system_time'] = \
        util.sysstats.proc_cpu_system_time(cpid, ssh_client)

    common_statistics['controller_cpu_user_time'] = \
        util.sysstats.proc_cpu_user_time(cpid, ssh_client)
    common_statistics['controller_vm_size'] = \
        util.sysstats.proc_vm_size(cpid, ssh_client)
    common_statistics['controller_num_fds'] = \
        util.sysstats.proc_num_fds(cpid, ssh_client)
    common_statistics['controller_num_threads'] = \
        util.sysstats.proc_num_threads(cpid, ssh_client)
    common_statistics['one_minute_load'] = util.sysstats.sys_load_average(ssh_client)[0]
    common_statistics['five_minute_load'] = util.sysstats.sys_load_average(ssh_client)[1]
    common_statistics['fifteen_minute_load'] = \
        util.sysstats.sys_load_average(ssh_client)[2]
    return common_statistics


