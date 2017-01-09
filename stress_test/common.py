# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Reusable functions for stress tests """

import json
import logging
import requests
import subprocess
import time
import util.cpu
import util.netutil
import util.sysstats

def check_ds_switches(controller_nb_interface):
    """Query number of switches registered in ODL operational DS

    :param controller_nb_interface: namedtuple containing 1) controller_node_ip
    2)controller_restconf_port 3) controller_restconf_user
    4) controller_restconf_password
    :returns: number of hosts found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    :type controller_nb_interface: namedtuple<str,int,str,str>
    """

    url = ('http://{0}:{1}/restconf/operational/network-topology:'
           'network-topology/network-topology:topology/flow:1/'.
           format(controller_nb_interface.ip, controller_nb_interface.port))
    auth_token = (controller_nb_interface.username,
                  controller_nb_interface.password)
    s = requests.Session()
    s.trust_env = False
    logging.debug('[check_ds_switches] Making RestCall: {0}'.format(url))
    try:
        datastore = s.get(url=url, auth=auth_token).json()['topology'][0]
    except:
        logging.error('[check_ds_switches] Fail getting response from '
                      'operational datastore')
        return -1

    switches = [node for node in datastore.get('node', []) if not node['node-id'].startswith('host:')]
    logging.debug('[check_ds_switches] Discovered switches: {0}'.
                  format(len(switches)))
    return len(switches)

def command_exec_wrapper(cmd_list, prefix='', ssh_client=None,
                         data_queue=None):
    """Executes a command either locally or remotely and returns the result

    :param cmd_list: the command to be executed given in a list format of
    command and its arguments
    :param prefix: The prefix to be used for logging of executed command output
    :param ssh_client : SSH client provided by paramiko to run the command
    :param data_queue: data queue where generator output is posted line by line
    the generator process will run.
    :returns: The commands exit status
    :rtype: int
    :type cmd_list: list<str>
    :type prefix: str
    :type ssh_client: paramiko.SSHClient
    :type data_queue: multiprocessing.Queue
    """

    if ssh_client == None:
        exit_status = util.customsubprocess.check_output_streaming(cmd_list,
            prefix, data_queue)
    else:
        exit_status = util.netutil.ssh_run_command(ssh_client,
            ' '.join(cmd_list), prefix, data_queue)[0]
    return exit_status

def generate_json_results(results, out_json):
    """ Creates the result json file and writes test results in it

    :param results A list containing the results.
    :param out_json: The file path of json file to be created and write
    results in it
    :type results: <list<dictionary>>
    :type out_json: str
    """

    try:
        if len(results) > 0:
            with open(out_json, 'w') as ojf:
                json.dump(results, ojf)
                ojf.close()
                logging.info('[generate_json_results] Results written to {0}.'.
                             format(out_json))
        else:
            logging.error('[generate_json_results] results parameter was empty.'
                          ' Nothing to be saved')
    except:
        logging.error('[generate_json_results] output json file could not be '
                      'created. Check privileges.')


