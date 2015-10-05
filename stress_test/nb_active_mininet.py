# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NorthBound Performance test """

import common
import controller_utils
import flow_utils
import ipaddress
import itertools
import json
import logging
import mininet_utils
import multiprocessing
import os
import report_spec
import requests
import shutil
import sys
import time
import util.customsubprocess
import util.process
import util.file_ops
import util.cpu
import util.netutil


def get_node_names(ctrl_ip, ctrl_port, auth_token):
    """
    Fetch node names from the OpenDaylight operational DS

    :param ctrl_ip: controller IP
    :param ctrl_port: controller RESTconf port
    :param auth_token: RESTconf authorization token (username/password tuple)
    :returns: list with node names registered in operational DS
    :rtype:
    :type ctrl_ip: str
    :type ctrl_port: int
    :type auth_token: tuple<str>
    """

    getheaders = {'Accept': 'application/json'}
    url_request = ('http://{0}:{1}/restconf/operational/network-topology:'
                   'network-topology/network-topology:topology/flow:1'.
                   format(ctrl_ip, ctrl_port))
    node_names = []
    session = requests.Session()
    while True:
        logging.debug(
            '[flow_master_thread] Trying to fetch node names from datastore')
        request = session.get(url_request, headers=getheaders, stream=False,
                              auth=auth_token)
        json_topology = json.loads(request.text)
        nodes = json_topology.get('topology')[0].get('node')
        if nodes is not None:
            break

    for node in nodes:
        node_names.append(node.get('node-id'))

    return node_names



def distribute_workload(nnodes, nflows, opqueues, operation, node_names):
    """
    Creates operations of the form (operation, 'target_switch', uid,
    'IP_address'), one for each flow, and distributes them in a round robin
    fashion to the worker queues.

    The operation can be a flow ADD or REMOVE. The target_switch is the switch
    on which the operation will be applied. The uid is a unique id for the
    operation. IP_adress is the IP address that will populate the destination
    IP of the flow created by a template.

    :param nnodes: number of nodes (switches) to generate operations for
    Flows will be added to nodes [0, n-1]
    :param nflows: total number of flows to distribute
    :param opqueues: workers operation queues
    :param operation: operation to perform (Add or Remove)
    :param node_names: array Name of each node in Opendaylight Datastore.
    :type nnodes: int
    :type nflows: int
    """

    curr_ip = ipaddress.ip_address('0.0.0.0')
    nworkers = len(opqueues)

    for flow in range(0, nflows):
        dest_node = flow % nnodes
        node_name = node_names[dest_node]
        operation_info = (operation, node_name, flow, curr_ip.compressed)

        qid = (dest_node - 1) % nworkers
        opqueues[qid].put(operation_info)

        curr_ip = curr_ip + 1


def flow_worker_thread(wid, opqueue, resqueue, flow_template, url_template,
                       op_delay_ms, auth_token):
    """
    Function executed by flow worker thread

    :param wid: worker id
    :param opqueue: queue where flow master will issue operations
    :param resqueue:
    :param flow_template: template from which flows are created
    :param url_template: template for the url of the REST call
    :param op_delay_ms: delay between thread operations (in milliseconds)
    :param auth_token: RESTconf authorization token (username/password tuple)
    :type wid: int
    :type opqueue: multiprocessing.Queue
    :type resqueue: multiprocessing.Queue
    :type flow_template: str
    :type url_template: str
    :type op_delay_ms: int
    :type auth_token: tuple<str>
    """

    logging.debug('[flow_worker_thread] Worker {0} initiating.'.format(wid))

    flow_processor = flow_utils.FlowProcessor(flow_template, url_template,
                                              auth_token)
    failed_flow_ops = 0

    # Read request from queue
    # Op type could be A/D/T, for add/deletion and termination respectively.
    while True:
        op_type,of_node,flow_id,current_ip = opqueue.get(block=True,
                                                         timeout=10000)
        logging.debug(
            '[flow_worker_thread] Worker {0}, received operation'
            ' = ( OP = {1}, Node = {2}, Flow-id = {3})'.format(wid, op_type,
                                                               of_node,
                                                               flow_id))

        if op_type == 'T':
            logging.debug('[flow_worker_thread] '
                          'Worker {0} will terminate.'.format(wid))
            resqueue.put(failed_flow_ops)
            return

        elif op_type == 'A':
            status = flow_processor.add_flow(flow_id, of_node, current_ip)
            logging.debug('[flow_worker_thread] [op_type]: op_type = A '
                          '(Adding flow)| Status code of the response: '
                          '{0}.'.format(status))
            if status != 200:
                failed_flow_ops += 1

        elif op_type == 'D':
            status = flow_processor.remove_flow(flow_id, of_node)
            logging.debug('[flow_worker_thread] [op_type]: op_type = D '
                          '(Remove flow)| Status code of the response: '
                          '{0}.'.format(status))
            if status != 200:
                failed_flow_ops += 1

        time.sleep(float(op_delay_ms)/1000)



def create_workers(nworkers, flow_template, url_template, op_delay_ms,
                   auth_token):
    """
    Creates flow workers as separate processes along with their queues.

    :param nworkers: number of workers to create
    :param flow_template: template from which flows are created
    :param url_template: Url in which each worker will issue flows.
    :param op_delay_ms: delay between flow operations in each worker
    (in milliseconds)
    :param auth_token: RESTconf authorization token (username/password tuple)
    :returns: worker queues and worker threads
    :type nworkers: int
    :type flow_templates: str
    :type url_template: str
    :type worker_delay: int
    :type auth_token: tuple<str>
    """

    opqueues = []
    wthr = []
    resqueues = []

    for wid in range(0, nworkers):
        opqueue = multiprocessing.Queue()
        resqueue = multiprocessing.Queue()
        opqueues.append(opqueue)
        resqueues.append(resqueue)
        worker = multiprocessing.Process(target=flow_worker_thread,
                                         args=(wid, opqueue, resqueue,
                                               flow_template, url_template,
                                               op_delay_ms, auth_token))
        wthr.append(worker)

    return opqueues, wthr, resqueues


def join_workers(opqueues, resqueues, wthr):
    """
    Terminates all workers by sending a T operation.

    :param opqueues: workers operation queues
    :param resqueues: workers result queues
    :param wthr: worker thread objects
    """

    for curr_queue in opqueues:
        curr_queue.put(('T', 0, 0, '0'))

    for worker in wthr:
        worker.join()

    failed_flow_ops = 0
    for resqueue in resqueues:
        failed_flow_ops += resqueue.get(block=True)

    logging.debug('[flow_master_thread] {0} workers terminated.'.
                  format(len(opqueues)))
    return failed_flow_ops



def poll_flows(expected_flows, ctrl_ip, ctrl_port, discovery_deadline_ms,
               t_start, auth_token):
    """
    Monitors operational DS until the expected number of flows are found or the
    deadline is reached.

    :param expected_flows: expected number of flows
    :param ctrl_ip: controller IP
    :param ctrl_port: controller RESTconf port
    :param discovery_deadline_ms: discover deadline (in milliseconds)
    :param t_start: timestamp for begin of discovery
    :param auth_token: RESTconf authorization token (username/password tuple)

    :returns: Returns a float number containing the time in which
    expected_flows were discovered otherwise containing -1.0 on failure.
    :rtype: float
    :type expected_flows: int
    :type ctrl_ip: str
    :type ctrl_port: int
    :type discovery_deadline_ms: int
    :type t_start: float
    """

    deadline = float(discovery_deadline_ms)/1000
    odl_inventory = flow_utils.FlowExplorer(ctrl_ip, ctrl_port, 'operational',
                                            auth_token)
    t_discovery_start = time.time()

    while True:
        if (time.time() - t_discovery_start) > deadline:
            logging.info('[flow_master_thread] Deadline of {0} seconds '
                         'passed'.format(deadline))
            return -1.0

        else:
            odl_inventory.get_inventory_flows_stats()
            logging.debug('Found {0} flows at inventory'.
                          format(odl_inventory.found_flows))
            if odl_inventory.found_flows == expected_flows:
                time_interval = time.time() - t_start
                logging.info('[flow_master_thread] Flow-Master '
                             '{0} flows found in {1} seconds'.
                             format(expected_flows, time_interval))

                return time_interval

        time.sleep(1)


def flow_master_thread(mqueue, ctrl_ip, ctrl_port, nflows, nnodes, nworkers,
                       flow_template, op_delay_ms, delete_flag,
                       discovery_deadline_ms, auth_token):
    """Function executed by flow master thread.

    :param mqueue: queue where the flow master thread returns results to the
    main context
    :param ctrl_ip: controller IP
    :param ctrl_port: controller RESTconf port
    :param nnodes: number of nodes (switches) to generate operations for.
    Flows will be added to nodes [0, n-1]
    :param nflows: total number of flows to distribute
    :param nworkers: number of worker threads to create
    :param flow_template: template from which flows are created
    :param op_delay_ms: delay between thread operations (in milliseconds)
    :param delete_flag: whether to delete or not the added flows as part of the
    test
    :param discovery_deadline_ms: deadline for flow discovery (in milliseconds)
    :param auth_token: RESTconf authorization token (username/password tuple)
    :type mqueue: multiprocessing.Queue
    :type ctrl_ip:
    :type ctrl_port: int
    :type nflows: int
    :type nnodes: int
    :type nworkers: int
    :type flow_template:
    :type op_delay_ms: int
    :type delete_flag: bool
    :type discovery_deadline_ms: int
    :type auth_token: tuple<str>
    """

    results = []
    failed_flow_ops = 0

    logging.info('[flow_master_thread] Initializing. Will perform {0} flow '
                 'operations at {1} openflow nodes with {2} workers'.format(
                 nflows, nnodes, nworkers))

    url_template = 'http://' + ctrl_ip + ':' + ctrl_port + \
        '/' + 'restconf/config/opendaylight-inventory:nodes/node/%s/' + \
        'table/0/flow/%d'

    logging.info('[flow_master_thread] Creating workers for ADD ops')
    opqueues, wthr, resqueues = create_workers(nworkers, flow_template,
                                               url_template, op_delay_ms,
                                               auth_token)
    node_names = get_node_names(ctrl_ip, ctrl_port, auth_token)

    logging.debug('[flow_master_thread] Distributing workload')
    distribute_workload(nnodes, nflows, opqueues, 'A', node_names)

    logging.debug('[flow_master_thread] Starting workers')
    t_start = time.time()
    for worker_thread in wthr:
        worker_thread.start()

    logging.debug('[flow_master_thread] Joining workers')
    failed_flow_ops += join_workers(opqueues, resqueues, wthr)

    logging.debug('[flow_master_thread] Initiate flow polling')
    addition_time = poll_flows(nflows, ctrl_ip, ctrl_port,
                               discovery_deadline_ms, t_start, auth_token)

    results.append(addition_time)

    if delete_flag:
        logging.info('[flow_master_thread] Creating workers for DEL ops')
        opqueues, wthr, resqueues = create_workers(nworkers, flow_template,
                                                   url_template, op_delay_ms,
                                                   auth_token)

        logging.debug('[flow_master_thread] Distributing workload')
        distribute_workload(nnodes, nflows, opqueues, 'D', node_names)

        logging.debug('[flow_master_thread] Starting workers')
        t_start = time.time()
        for worker_thread in wthr:
            worker_thread.start()

        logging.debug('[flow_master_thread] Joining workers')
        failed_flow_ops += join_workers(opqueues, resqueues, wthr)

        logging.debug('[flow_master_thread] Initiate flow polling')
        deletion_time = poll_flows(0, ctrl_ip, ctrl_port, discovery_deadline_ms,
                                   t_start, auth_token)
        results.append(deletion_time)

    results.append(failed_flow_ops)
    mqueue.put(results)
    return


def mininet_topo_check_booted(expected_switches, mininet_group_size,
                              mininet_group_delay_ms,
                              mininet_get_switches_handler, mininet_ip,
                              mininet_rest_server_port, ctrl_ip,
                              ctrl_port, auth_token, num_tries=3):
    """
    Check if a Mininet topology has been booted. Check both from the Mininet
    side and from the controller operational DS.

    :param expected_switches: expected Mininet switches
    :param mininet_group_size: group size at which switches where added in a
    Mininet topo
    :param mininet_group_delay_ms: delay between group additions
    (in milliseconds)
    :param mininet_get_switches_handler: Mininet handler used to query the
    current number of switches in a Mininet topology
    :param mininet_ip: Mininet node IP
    :param mininet_rest_server_port: port of the Mininet node REST server
    :param ctrl_ip: controller IP
    :param ctrl_port: controller RESTconf port
    :param auth_token: RESTconf authorization token (username/password tuple)
    :param num_tries: maximum number of tries until the method identifies that
    number of discovered switches of the Mininet topology is equal to the
    number of expected Mininet switches
    :raises Exception: If we reach max number of tries and either the
    controller has not seen the topology or the topology has failed to start.
    :type expected_switches: int
    :type mininet_group_size: int
    :type mininet_group_delay_ms: int
    :type mininet_get_switches_handler: str
    :type mininet_ip: str
    :type mininet_rest_server_port: int
    :type ctrl_ip: str
    :type ctrl_port: int
    :type auth_token: tuple<str>
    :type num_tries: int
    """

    mininet_group_delay = float(mininet_group_delay_ms)/1000
    discovered_switches = 0
    ds_switches = 0
    tries = 0
    while tries < num_tries:
        logging.info('[mininet_topo_check_booted] Check if topology is up.')

        # Here we sleep in order to give time to the controller to discover
        # topology through the LLDP protocol.
        time.sleep(int(expected_switches/mininet_group_size) * \
                   mininet_group_delay + 15)
        outq = multiprocessing.Queue()

        try:
            util.customsubprocess.check_output_streaming(
                [mininet_get_switches_handler, mininet_ip,
                 str(mininet_rest_server_port)],
                '[mininet_get_switches_handler]', queue=outq)
            discovered_switches = int(outq.get().strip())
            logging.info('[mininet_topo_check_booted] Discovered {0} switches'
                          ' at the Mininet side'.format(discovered_switches))

            ds_switches = common.check_ds_switches(ctrl_ip, ctrl_port,
                                                   auth_token)
            logging.info('[mininet_topo_check_booted] Discovered {0} switches'
                          ' at the controller side'.format(ds_switches))
            if discovered_switches == expected_switches and \
                ds_switches == expected_switches and expected_switches != 0:
                return

        except:
            pass

        tries += 1

    raise Exception('Topology did not fully initialized. Expected {0} '
                    'switches, but found {1} at the Mininet side and {2} '
                    'at the controller side.'.
                    format(expected_switches, discovered_switches,
                           ds_switches))


def nb_active_mininet_run(out_json, ctrl_base_dir, mininet_base_dir, conf,
                          output_dir):
    """Run NB active test with Mininet.

    :param out_json: the JSON output file
    :param ctrl_base_dir: controller base directory
    :param mininet_base_dir: mininet base directory
    :param conf: JSON configuration dictionary
    :param output_dir: directory to store output files
    :type out_json: str
    :type ctrl_base_dir: str
    :type mininet_base_dir: str
    :type conf: dict
    :type output_dir: str
    """

    f_temp = """{
        "flow-node-inventory:flow": [
            {
                "flow-node-inventory:cookie": %d,
                "flow-node-inventory:cookie_mask": 4294967295,
                "flow-node-inventory:flow-name": "%s",
                "flow-node-inventory:hard-timeout": %d,
                "flow-node-inventory:id": "%s",
                "flow-node-inventory:idle-timeout": %d,
                "flow-node-inventory:installHw": true,
                "flow-node-inventory:instructions": {
                    "flow-node-inventory:instruction": [
                        {
                            "flow-node-inventory:apply-actions": {
                                "flow-node-inventory:action": [
                                    {
                                        "flow-node-inventory:drop-action": {},
                                        "flow-node-inventory:order": 0
                                    }
                                ]
                            },
                            "flow-node-inventory:order": 0
                        }
                    ]
                },
                "flow-node-inventory:match": {
                    "flow-node-inventory:ipv4-destination": "%s/32",
                    "flow-node-inventory:ethernet-match": {
                        "flow-node-inventory:ethernet-type": {
                            "flow-node-inventory:type": 2048
                        }
                    }
                },
                "flow-node-inventory:priority": 1,
                "flow-node-inventory:strict": false,
                "flow-node-inventory:table_id": 0
            }
        ]
       }"""

    # Global variables read-write shared between monitor and main thread
    global_sample_id = 0
    cpid = 0
    test_type = '[nb_active_mininet]'

    logging.info('{0} Initializing test parameters.'.format(test_type))
    controller_build_handler = ctrl_base_dir + conf['controller_build_handler']
    controller_start_handler = ctrl_base_dir + conf['controller_start_handler']
    controller_status_handler = \
        ctrl_base_dir + conf['controller_status_handler']
    controller_stop_handler = ctrl_base_dir + conf['controller_stop_handler']
    controller_clean_handler = ctrl_base_dir + conf['controller_clean_handler']
    controller_statistics_handler = \
        ctrl_base_dir + conf['controller_statistics_handler']
    controller_logs_dir = ctrl_base_dir + conf['controller_logs_dir']
    controller_restart = conf['controller_restart']
    controller_ip = conf['controller_ip']
    controller_port = conf['controller_port']
    controller_restconf_port = conf['controller_restconf_port']
    auth_token = (conf['controller_restconf_user'],
                  conf['controller_restconf_password'])
    controller_rebuild = conf['controller_rebuild']
    controller_cpu_shares = conf['controller_cpu_shares']
    controller_cleanup = conf['controller_cleanup']

    mininet_boot_handler = mininet_base_dir + conf['mininet_boot_handler']
    mininet_stop_switches_handler = mininet_base_dir + \
        conf['mininet_stop_switches_handler']
    mininet_get_switches_handler = mininet_base_dir + \
        conf['mininet_get_switches_handler']
    mininet_init_topo_handler = mininet_base_dir + \
        conf['mininet_init_topo_handler']
    mininet_start_topo_handler = mininet_base_dir + \
        conf['mininet_start_topo_handler']
    mininet_server_remote_path = \
        '/tmp/transfered_files/mininet/mininet_custom_boot.py'
    mininet_ip = conf['mininet_ip']
    mininet_ssh_port = conf['mininet_ssh_port']
    mininet_rest_server_port = conf['mininet_rest_server_port']
    mininet_username = conf['mininet_username']
    mininet_password = conf['mininet_password']
    flow_delete_flag = conf['flow_delete_flag']

    # list of samples: each sample is a dictionary that contains
    # all information that describes a single measurement, i.e.:
    #    - the actual performance results
    #    - secondary runtime statistics
    #    - current values of test dimensions (dynamic)
    #    - test configuration options (static)
    total_samples = []

    try:
        logging.info(
            '{0} Initiating SSH session with Mininet node.'.format(test_type))
        mn_session = util.netutil.ssh_connect_or_return(mininet_ip,
                                                        mininet_username,
                                                        mininet_password, 10,
                                                        mininet_ssh_port)

        util.netutil.create_remote_directory(mininet_ip, mininet_username,
                                             mininet_password,
                                             '/tmp/transfered_files/',
                                             mininet_ssh_port)

        logging.info('{0} Copying handlers to Mininet VM'.format(test_type))
        mininet_utils.copy_mininet_handlers(mininet_ip, mininet_username,
                                  mininet_password, mininet_base_dir,
                                  '/tmp/transfered_files/', mininet_ssh_port)

        # Define CPU affinity for controller.
        # CPUs for generator are not used here.
        controller_cpus_str, generator_cpus_str = \
            common.create_cpu_shares(controller_cpu_shares, 0)

        util.file_ops.check_filelist([controller_build_handler,
            controller_start_handler, controller_status_handler,
            controller_stop_handler, controller_clean_handler,
            controller_statistics_handler, mininet_boot_handler,
            mininet_stop_switches_handler, mininet_get_switches_handler,
            mininet_start_topo_handler, mininet_init_topo_handler])

        if controller_rebuild:
            logging.info('{0} Building controller.'.format(test_type))
            controller_utils.rebuild_controller(controller_build_handler)

        controller_utils.check_for_active_controller(controller_port)

        os.environ['JAVA_OPTS'] = ' '.join(conf['java_opts'])

        logging.info(
            '{0} Starting and stopping controller to generate xml files'.
            format(test_type))
        cpid = controller_utils.start_controller(controller_start_handler,
                                   controller_status_handler, controller_port,
                                   controller_cpus_str)
        logging.info('{0} OK, controller status is 1.'.format(test_type))
        controller_utils.stop_controller(controller_stop_handler,
            controller_status_handler, cpid)

        # Run tests for all possible dimensions
        for (total_flows,
             flow_operations_delay_ms,
             mininet_size,
             flow_workers,
             mininet_group_size,
             mininet_group_delay_ms,
             mininet_hosts_per_switch,
             mininet_topology_type,
             controller_statistics_period_ms) in \
             itertools.product(conf['total_flows'],
                               conf['flow_operations_delay_ms'],
                               conf['mininet_size'],
                               conf['flow_workers'],
                               conf['mininet_group_size'],
                               conf['mininet_group_delay_ms'],
                               conf['mininet_hosts_per_switch'],
                               conf['mininet_topology_type'],
                               conf['controller_statistics_period_ms']):

            controller_utils.controller_changestatsperiod(
                controller_statistics_handler, controller_statistics_period_ms)

            logging.info('{0} Booting up Mininet REST server.'.
                          format(test_type))
            mininet_utils.start_mininet_server(mn_session,
                mininet_server_remote_path, mininet_ip,
                mininet_rest_server_port)

            logging.info('{0} Starting controller.'.format(test_type))
            cpid = controller_utils.start_controller(
                controller_start_handler, controller_status_handler,
                controller_port, controller_cpus_str)

            logging.info('{0} OK, controller status is 1.'.format(test_type))
            logging.debug(
                '{0} Creating flowmaster result queue.'.format(test_type))

            # The queue where flowmaster will return its results.
            mqueue = multiprocessing.Queue()
            logging.info(
                '{0} Initializing topology on REST server.'.format(test_type))
            mininet_utils.init_mininet_topo(mininet_init_topo_handler,
                mininet_ip, mininet_rest_server_port, controller_ip,
                controller_port, mininet_topology_type, mininet_size,
                mininet_group_size, mininet_group_delay_ms,
                mininet_hosts_per_switch)

            logging.info('{0} Starting mininet topology.'.format(test_type))
            mininet_utils.stop_mininet_topo(mininet_start_topo_handler,
                mininet_ip, mininet_rest_server_port)

            mininet_topo_check_booted(mininet_size, mininet_group_size,
                                      mininet_group_delay_ms,
                                      mininet_get_switches_handler, mininet_ip,
                                      mininet_rest_server_port, controller_ip,
                                      controller_restconf_port, auth_token)

            flow_discovery_deadline_ms = 120000

            # Parallel section
            logging.info('{0} Creating flow master thread'.format(test_type))
            flowmaster_thread = multiprocessing.Process(
                                    target=flow_master_thread,
                                    args=(mqueue, controller_ip,
                                          str(controller_restconf_port),
                                          total_flows, mininet_size,
                                          flow_workers, f_temp,
                                          flow_operations_delay_ms,
                                          flow_delete_flag,
                                          flow_discovery_deadline_ms,
                                          auth_token))

            flowmaster_thread.start()
            res = mqueue.get(block=True)
            logging.info('{0} Joining flow master thread.'.format(test_type))
            flowmaster_thread.join()

            # Getting results
            statistics = common.sample_stats(cpid)
            statistics['global_sample_id'] = global_sample_id
            global_sample_id += 1
            statistics['controller_ip'] = controller_ip
            statistics['controller_port'] = str(controller_port)
            statistics['controller_restart'] = controller_restart
            statistics['total_flows'] = total_flows
            statistics['mininet_size'] = mininet_size
            statistics['mininet_topology_type'] = mininet_topology_type
            statistics['mininet_hosts_per_switch'] = \
                mininet_hosts_per_switch
            statistics['mininet_group_size'] = mininet_group_size
            statistics['mininet_group_delay_ms'] = mininet_group_delay_ms
            statistics['controller_statistics_period_ms'] = \
                controller_statistics_period_ms
            statistics['flow_operation_delay_ms'] = flow_operations_delay_ms
            statistics['flow_workers'] = flow_workers
            statistics['add_flows_time'] = res[0]
            if flow_delete_flag:
                statistics['delete_flows_time'] = res[1]
            statistics['failed_flow_operations'] = res[-1]
            statistics['flow_delete_flag'] = str(flow_delete_flag)
            total_samples.append(statistics)

            logging.debug('{0} Stopping mininet topology.'.format(test_type))
            mininet_utils.stop_mininet_topo(mininet_stop_switches_handler,
                mininet_ip, mininet_rest_server_port)

            logging.debug('{0} Stopping controller.'.format(test_type))
            controller_utils.stop_controller(controller_stop_handler,
                controller_status_handler, cpid)

            logging.debug('{0} Killing REST daemon in Mininet VM.'.
                          format(test_type))
            mininet_utils.stop_mininet_server(mn_session,
                                              mininet_rest_server_port)

    except:
        logging.error('{0} :::::::::: Exception :::::::::::'.format(test_type))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.error('{0} Exception: {1}, {2}.'.
                      format(test_type, exc_type, exc_tb.tb_lineno))
        logging.exception('')

        errors = str(exc_obj).rstrip().split('\n')
        for error in errors:
            logging.error('{0} {1}'.format(test_type, error))

    finally:
        logging.info('{0} Finalizing test.'.format(test_type))

        logging.info('{0} Creating test output dirctory if not exist.'.
                     format(test_type))
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if len(total_samples) > 0:
            with open(out_json, 'w') as ojf:
                json.dump(total_samples, ojf)
                ojf.close()

        try:
            logging.info('{0} Stopping controller.'.
                         format(test_type))
            controller_utils.stop_controller(controller_stop_handler,
                controller_status_handler, cpid)
        except:
            pass

        if os.path.isdir(controller_logs_dir):
            logging.info('{0} Collecting logs'.format(test_type))
            shutil.copytree(controller_logs_dir, output_dir + '/log')
            shutil.rmtree(controller_logs_dir)

        try:
            logging.info('{0} Tearing down any existend mininet topology.'.
                          format(test_type))
            mininet_utils.stop_mininet_topo(mininet_stop_switches_handler,
                mininet_ip, mininet_rest_server_port)
        except:
            pass

        try:
            logging.info('{0} Killing REST daemon in Mininet VM.'.
                          format(test_type))
            mininet_utils.stop_mininet_server(mn_session,
                                              mininet_rest_server_port)
        except:
            pass

        logging.info('{0} Delete handleres from Mininet VM.'.
                      format(test_type))
        mininet_utils.delete_mininet_handlers(mininet_ip, mininet_username,
                                    mininet_password,
                                    '/tmp/transfered_files/', mininet_ssh_port)
        mn_session.close()


def get_report_spec(test_type, config_json, results_json):
    """
    Return the report specification for this test

    :param test_type: test short description (title)
    :param config_json: JSON config path
    :param results_json: JSON results path
    :returns: report specification for this test
    :rtype: ReportSpec
    :type: test_type: str
    :type: config_json: str
    :type: results_json: str
    """

    report_spec_obj = report_spec.ReportSpec(
        config_json, results_json, '{0}'.format(test_type),
        [report_spec.TableSpec(
            '1d', 'Test configuration parameters (detailed)',
            [('controller_name', 'Controller name'),
             ('controller_build_handler', 'Controller build script'),
             ('controller_start_handler', 'Controller start script'),
             ('controller_stop_handler', 'Controller stop script'),
             ('controller_status_handler', 'Controller status script'),
             ('controller_clean_handler', 'Controller cleanup script'),
             ('controller_statistics_handler', 'Controller statistics script'),
             ('controller_ip', 'Controller IP address'),
             ('controller_port', 'Controller listening port'),
             ('controller_rebuild', 'Controller rebuild between test repeats'),
             ('controller_logs_dir', 'Controller log save directory'),
             ('controller_restconf_port', 'Controller RESTconf port'),
             ('mininet_boot_handler', 'Mininet boot handler'),
             ('mininet_stop_switches_handler',
              'Mininet stop switches handler'),
             ('mininet_get_switches_handler', 'Mininet get switches handler'),
             ('mininet_init_topo_handler',
              'Mininet initialize topology handler'),
             ('mininet_start_topo_handler', 'Mininet start topology handler'),
             ('mininet_ip', 'Mininet node IP'),
             ('mininet_rest_server_port', 'Mininet node REST server port'),
             ('mininet_size', 'Mininet network size'),
             ('mininet_topology_type', 'Mininet topology type'),
             ('mininet_hosts_per_switch', 'Mininet hosts per switch'),
             ('flow_workers', 'Flow worker threads'),
             ('total_flows', 'Total flows to be added'),
             ('flow_operations_delay_ms', 'Delay between flow operations'),
             ('flow_delete_flag', 'Flow delete flag'),
             ('java_opts', 'JVM options')], config_json)],
        [report_spec.TableSpec('2d', 'Test results',
            [('global_sample_id', 'Sample ID'),
             ('timestamp', 'Sample timestamp (seconds)'),
             ('date', 'Sample timestamp (date)'),
             ('total_flows', 'Total flow operations'),
             ('failed_flow_operations', 'Total failed flow operations'),
             ('add_flows_time', 'Add flows time (seconds)'),
             ('delete_flows_time', 'Delete flows time (seconds)'),
             ('flow_operation_delay_ms', 'Flow operation delay (milliseconds)'),
             ('flow_workers', 'Flow workers'),
             ('flow_delete_flag', 'Deletion flag'),
             ('mininet_size', 'Mininet Size'),
             ('mininet_topology_type', 'Mininet Topology Type'),
             ('mininet_hosts_per_switch', 'Mininet Hosts per Switch'),
             ('mininet_group_size', 'Mininet Group Size'),
             ('mininet_group_delay_ms', 'Mininet Group Delay (ms)'),
             ('controller_ip', 'Controller IP'),
             ('controller_port', 'Controller port'),
             ('controller_vm_size', 'Controller VM size'),
             ('controller_java_xopts', 'Java options'),
             ('free_memory_bytes', 'System free memory in bytes'),
             ('used_memory_bytes', 'System used memory in bytes'),
             ('total_memory_bytes', 'System total memory in bytes'),
             ('one_minute_load', 'One minute load'),
             ('five_minute_load', 'Five minutes load'),
             ('fifteen_minute_load', 'Fifteen minutes load'),
             ('controller_cpu_system_time', 'Controller CPU system time'),
             ('controller_cpu_user_time', 'Controller CPU user time'),
             ('controller_num_threads', 'Controller num of threads'),
             ('controller_num_fds', 'Controller num of fds'),
             ('controller_statistics_period_ms',
              'Controller statistics period (ms)')], results_json)])

    return report_spec_obj
