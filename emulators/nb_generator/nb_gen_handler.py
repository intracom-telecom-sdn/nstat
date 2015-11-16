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
import os
import requests
import subprocess
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

    generator_path = os.path.dirname(os.path.abspath(__file__))
    cmd = generator_path + ('/python3.4 nb_gen.py --controller-ip=\'{0}\' '
                            '--controller-port=\'{1}\' '
                            '--number-of-flows=\'{2}\' '
                            '--number-of-switches=\'{3}\' '
                            '--number-of-workers=\'{4}\' '
                            '--flow-template=\'{5}\' '
                            '--operation-delay=\'{6}\' '
                            '--discovery-deadline=\'{7}\' '
                            '--restconf-user=\'{8}\' '
                            '--restconf-password=\'{9}\'')
    if sys.argv[8] == 'True':
        cmd += ' --delete-flag'
    cmd = cmd.format(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
                     sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[9],
                     sys.argv[10], sys.argv[11])
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    cmd_output = p.stdout.read().decode(sys.stdout.encoding)
    cmd_output = cmd_output.strip()
    print(json.dumps(cmd_output))

if __name__ == '__main__':
    northbound_generator()
