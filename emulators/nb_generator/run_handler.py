#! /usr/bin/env python3.4

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Run handler of NorthBound traffic generator
"""
import json
import re
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
    6.  op_delay_ms: delay between thread operations (in milliseconds)
    7.  delete_flows_flag: whether to delete or not the added flows as part of
    the test
    8. controller_restconf_user: controller NorthBound RESTconf username
    9. controller_restconf_password: controller NorthBound RESTconf password
    10. logging_level: nb generator logging level (is passed from
    nstat orchestrator)
    """

    cmd = ('python3.4 nb_gen.py --controller-ip=\'{0}\' '
                            '--controller-port=\'{1}\' '
                            '--number-of-flows=\'{2}\' '
                            '--number-of-workers=\'{3}\' '
                            '--operation-delay=\'{4}\' '
                            '--restconf-user=\'{5}\' '
                            '--restconf-password=\'{6}\' '
                            '--logging-level=\'{7}\'')
    if sys.argv[6] == 'True':
        cmd += ' --delete-flows'
    cmd = cmd.format(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
                     sys.argv[5], sys.argv[7], sys.argv[8],
                     sys.argv[9])
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    cmd_output = p.stdout.read().decode(sys.stdout.encoding)
    cmd_output = cmd_output.strip()
    regex_result = re.search(r' = [0-9].*\/[0-9].*', cmd_output)
    if regex_result == None:
        sys.exit(1)
    result = [float(x) for x in regex_result.group()[2:].strip().split('/')]
    print(json.dumps(result))

if __name__ == '__main__':
    northbound_generator()
