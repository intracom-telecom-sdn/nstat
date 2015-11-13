#! /usr/bin/env python3.4

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Handler for requesting a Mininet REST server to start a Mininet topology on
the current node
"""
import json
import nb_gen
import requests
import sys

def northbound_generator():
    """
    Command line arguments:

    1.  ctrl_ip: controller IP
    2.  ctrl_port: controller RESTconf port
    3.  nnodes: number of nodes (switches) to generate operations for.
    Flows will be added to nodes [0, n-1]
    4.  nflows: total number of flows to distribute
    5.  nworkers: number of worker threads to create
    6.  flow_template: template from which flows are created
    7.  op_delay_ms: delay between thread operations (in milliseconds)
    8.  delete_flag: whether to delete or not the added flows as part of the
    test
    9.  discovery_deadline_ms: deadline for flow discovery (in milliseconds)
    10. auth_token: RESTconf authorization token (username/password tuple)
    """
    # Example
    # python3.4 nb_gen_handler "192.168.64.17" "8181" "100000" "10" "*.json" "100" "True" "240000" "admin" "admin"

    ctrl_ip = sys.argv[1]
    ctrl_port = sys.argv[2]
    nnodes = sys.argv[3]
    nflows = sys.argv[4]
    nworkers = sys.argv[5]
    flow_template = sys.argv[6]
    op_delay_ms = sys.argv[7]
    delete_flag = sys.argv[8]
    discovery_deadline_ms = sys.argv[9]
    auth_token = (sys.argv[10], sys.argv[11])
    print(nflows)
    nb_generator_results = flow_master_thread(ctrl_ip, ctrl_port, nnodes,
                                              nworkers, flow_template,
                                              op_delay_ms,
                                              delete_flag,
                                              discovery_deadline_ms,
                                              auth_token)
    print(json.dumps(nb_generator_results))

if __name__ == '__main__':
    northbound_generator()
