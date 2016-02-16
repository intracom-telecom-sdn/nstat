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
    :param url_template: url in which each worker will issue flows.
    :param op_delay_ms: delay between flow operations in each worker
    (in milliseconds)
    :param auth_token: RESTconf authorization token (username/password tuple)
    :returns: worker queues (operational, result) and worker threads
    :rtype tuple<lst<multiprocessing.Queue()>>
    :type nworkers: int
    :type flow_template: str
    :type url_template: str
    :type op_delay_ms: int
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

    return (opqueues, wthr, resqueues)


def flow_worker_thread(wid, opqueue, resqueue, flow_template, url_template,
                       op_delay_ms, auth_token):
    """
    Function executed by flow worker thread

    :param wid: worker id
    :param opqueue: queue where flow master will issue operations
    :param resqueue:queue where flow master will issue operations
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
    :type opqueues: list<multiprocessing.Queue>
    :type operation: str
    :type nodenames: list<str>
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
    :returns: failed_flow_ops
    :rtype: failed_flow_ops int
    :type: opqueues list<multiprocessing.Queue>
    :type: resqueues list<multiprocessing.Queue>
    :type: wthr
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

def poll_flows(expected_flows, ctrl_ip, ctrl_port, t_start, auth_token):
    """
    Monitors operational DS until the expected number of flows are found or the
    deadline is reached.

    :param expected_flows: expected number of flows
    :param ctrl_ip: controller IP
    :param ctrl_port: controller RESTconf port
    :param t_start: timestamp for begin of discovery
    :param auth_token: RESTconf authorization token (username/password tuple)

    :returns: Returns a float number containing the time in which
    expected_flows were discovered otherwise containing -1.0 on failure.
    :rtype: float
    :type expected_flows: int
    :type ctrl_ip: str
    :type ctrl_port: int
    :type t_start: float
    :type auth_token: tuple<str>
    """

    deadline = 240
    odl_inventory = flow_utils.FlowExplorer(ctrl_ip, ctrl_port, 'operational',
                                            auth_token)
    t_discovery_start = time.time()
    previous_discovered_flows = 0

    while True:
        if (time.time() - t_discovery_start) > deadline:
            logging.info('[flow_master_thread] Deadline of {0} seconds '
                         'passed'.format(deadline))
            return -1.0

        else:
            odl_inventory.get_inventory_flows_stats()
            logging.debug('Found {0} flows at inventory'.
                          format(odl_inventory.found_flows))
            if odl_inventory.found_flows > previous_discovered_flows:
                t_discovery_start = time.time()
                previous_discovered_flows = odl_inventory.found_flows
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
    :rtype: node_names: list<str>
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
                              auth=(auth_token.controller_restconf_user,
                                    auth_token.controller_restconf_password))
        json_topology = json.loads(request.text)
        nodes = json_topology.get('topology')[0].get('node')
        if nodes is not None:
            break

    for node in nodes:
        node_names.append(node.get('node-id'))

    return node_names

def flow_ops_calc_time(opqueues, resqueues, wthr, nflows, ctrl_ip, ctrl_port,
                       auth_token):
    """Calculates transmission_interval, operation_time, failed_flow_ops
    :param opqueues: workers operation queues
    :param resqueues: workers result queues
    :param wthr: worker threads
    :param nflows:
    :param ctrl_ip:
    :param ctrl_port:
    :param auth_token:
    :returns (transmission_interval, operation_time, failed_flow_ops):
    transmission interval: time interval between requested flow operations
    operation time: total time
    failed flow operations:
    :rtype tuple<str>
    :type opqueues: list<multiprocessing.Queue()>
    :type resqueues: list<multiprocessing.Queue()>
    :type wthr: list<multiprocessing.Process()>
    :type nflows: int
    :type ctrl_ip: str
    :type ctrl_port: str
    :type auth_token: tuple<str>
    """
    failed_flow_ops = 0

    logging.info('[flow_master_thread] starting workers')
    t_start = time.time()

    for worker_thread in wthr:
        worker_thread.start()

    logging.info('[flow_operations_calc_time] joining workers')
    failed_flow_ops += join_workers(opqueues, resqueues, wthr)
    t_stop = time.time()
    transmission_interval = t_stop - t_start

    logging.info('[flow_operations_calc_time] initiate flow polling')
    operation_time = poll_flows(nflows, ctrl_ip, ctrl_port, t_start,
                                auth_token)

    return (transmission_interval, operation_time, failed_flow_ops)

def flow_ops_calc_time_run(flow_ops_params, op_delay_ms, node_names,
                           url_template, flow_template, auth_token,
                           delete_flows_flag=False):

    """Function executed by flow_master method
    :param flow_ops_params: namedtuple ['ctrl_ip', 'ctrl_port', 'nflows',
    'nworkers', 'discovery_deadline_ms'], (controller IP, controller RESTconf port,
    total number of flows to distribute, number of worker threads to create,
    deadline for flow discovery (in milliseconds)
    :param op_delay_ms: delay between thread operations (in milliseconds)
    :param node_names: list with node names registered in operational DS
    :param url_template: url for REST request to add/delete flows in
    controller's operational DS
    :param flow_template: template of flow in json form to be added/deleted in
    controller's operational DS
    :param auth_token: token containing restconf username/password used for
    REST requests in controller's operational DS
    :param delete_flows_flag: whether to delete or not the added flows as part
    of the test
    :returns tuple with transmission_interval, operation_time, failed_flow_ops
    transmission interval: time interval between requested flow operations
    operation time: total time
    failed flow operations:
    :rtype: tuple:
    :type ctrl_ip: str
    :type ctrl_port: str
    :type nflows: int
    :type nworkers: int
    :type discovery_deadline_ms: int
    :type op_delay_ms: int
    :type node_names:  list<str>
    :type url_template: str
    :type flow_template: str
    :type auth_token: tuple<str>
    :type delete_flows_flag: bool
    """

    operations_log_message = 'ADD'
    operations_type = 'A'

    if delete_flows_flag:
        operations_log_message = 'DEL'
        operation_type = 'D'

    logging.info('[flow_ops_calc_time_run] initializing: will perform {0} flow '
                 'operations at {1} openflow nodes with {2} workers'.format(
                 flow_ops_params.nflows, len(node_names),
                 flow_ops_params.nworkers))

    logging.info('[flow_ops_calc_time_run] creating workers for {0} ops'.
                 format(operations_log_message))

    opqueues, wthr, resqueues = create_workers(flow_ops_params.nworkers,
                                               flow_template, url_template,
                                               op_delay_ms, auth_token)

    logging.info('[flow_ops_calc_time_run] distributing workload')
    distribute_workload(flow_ops_params.nflows, opqueues,
                        operations_type, node_names)

    transmission_interval, operation_time, failed_flow_ops =  \
    flow_ops_calc_time(opqueues, resqueues, wthr, flow_ops_params.nflows,
                       flow_ops_params.ctrl_ip, flow_ops_params.ctrl_port,
                       auth_token)

    return (transmission_interval, operation_time, failed_flow_ops)
