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
import os
import re
import subprocess
import sys


def northbound_generator():
    """
    Command line arguments:

    1.  ctrl_ip: controller IP
    2.  ctrl_port: controller RESTconf port
    3.  nflows: total number of flows to distribute
    4.  nworkers: number of worker threads to create
    5.  op_delay_ms: delay between thread operations (in milliseconds)
    6.  delete_flows_flag: whether to delete or not the added flows as part of
    the test
    7. controller_restconf_user: controller NorthBound RESTconf username
    8. controller_restconf_password: controller NorthBound RESTconf password
    9. flows-per-request, the number of flows that will be sent in a single
    request
    10. logging_level: nb generator logging level (is passed from
    nstat orchestrator)
    """

    venv = 'source /opt/venv_nstat/bin/activate'
    if os.path.isfile(venv) is False:
        venv = ''
    else:
        venv+=';'

    cmd = ('{0} python3.4 nb_gen.py --controller-ip=\'{1}\' '
           '--controller-port=\'{2}\' '
           '--number-of-flows=\'{3}\' '
           '--number-of-workers=\'{4}\' '
           '--operation-delay=\'{5}\' '
           '--restconf-user=\'{6}\' '
           '--restconf-password=\'{7}\' '
           '--fpr={8} '
           '--logging-level=\'{9}\'')

    if sys.argv[6] == 'True':
        cmd += ' --delete-flows'
    cmd = cmd.format(venv, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
                     sys.argv[5], sys.argv[7], sys.argv[8],
                     sys.argv[9], sys.argv[10])
    p = subprocess.Popen(cmd, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)

    cmd_output = p.stdout.read().decode(sys.stdout.encoding)
    cmd_output = cmd_output.strip()
    regex_result = re.search(r"Total_failed_flows = [0-9].*", cmd_output)
    if regex_result is None:
        sys.exit(1)
    # 21: is the string offset from expression "Total_failed_flows =
    # " to extract the results
    result = [float(x) for x in regex_result.group()[21:].strip().split('/')]
    print(json.dumps(result))

if __name__ == '__main__':
    northbound_generator()
