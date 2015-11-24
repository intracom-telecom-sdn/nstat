# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Helper functions for NorthBound traffic generator """

import flow_utils
import ipaddress
import json
import logging
import multiprocessing
import requests
import time

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


def distribute_workload(nflows, opqueues, operation, node_names):
    """
    Creates operations of the form (operation, 'target_switch', uid,
    'IP_address'), one for each flow, and distributes them in a round robin
    fashion to the worker queues.

    The operation can be a flow ADD or REMOVE. The target_switch is the switch
    on which the operation will be applied. The uid is a unique id for the
    operation. IP_adress is the IP address that will populate the destination
    IP of the flow created by a template.

    :param nflows: total number of flows to distribute
    :param opqueues: workers operation queues
    :param operation: operation to perform (Add 'A' or Delete 'D')
    :param node_names: array Name of each node in Opendaylight datastore.
    :type nflows: int
    :type opqueues: <queue>
    :type operation: str
    :type nodenames: <list>
    """

    curr_ip = ipaddress.ip_address('0.0.0.0')
    nworkers = len(opqueues)
    nnodes = len(node_names)

    for flow in range(0, nflows):
        dest_node = flow % nnodes
        node_name = node_names[dest_node]
        operation_info = (operation, node_name, flow, curr_ip.compressed)

        qid = (dest_node - 1) % nworkers
        opqueues[qid].put(operation_info)

        curr_ip = curr_ip + 1


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
                logging.debug('[flow_master_thread] Flow-Master '
                             '{0} flows found in {1} seconds'.
                             format(expected_flows, time_interval))

                return time_interval

        time.sleep(1)

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


def flow_operations_add_delete(,delete_flag=False)

    create_workers_log_message = 'ADD'
    operation_type = 'A'

    if delete_flag:
        create_workers_log_message = 'DEL'
        operation_type = 'D'



    logging.info('[flow_master_thread] Initializing. Will perform {0} flow '
                 'operations at {1} openflow nodes with {2} workers'.format(
                 nflows, len(node_names), nworkers))

    logging.info('[flow_master_thread] Creating workers for {0} ops').
    format(create_workers_log_message)


    opqueues, wthr, resqueues = nb_gen_utils.create_workers(nworkers,
        flow_template, url_template, op_delay_ms, auth_token)

    logging.info('[flow_master_thread] Distributing workload')
    nb_gen_utils.distribute_workload(nflows, opqueues, '%', node_names)

    logging.info('[flow_master_thread] Starting workers')
    t_start = time.time()

    for worker_thread in wthr:
        worker_thread.start()

    logging.info('[flow_master_thread] Joining workers')
    failed_flow_ops += nb_gen_utils.join_workers(opqueues, resqueues, wthr)
    t_stop = time.time()
    transmission_interval = t_stop - t_start
    results.append(transmission_interval)

    logging.info('[flow_master_thread] Initiate flow polling')

    operation_time = nb_gen_utils.poll_flows(nflows, ctrl_ip, ctrl_port,
                                             discovery_deadline_ms, t_start,
                                             auth_token)
    results.append(operation_time)

    return results
