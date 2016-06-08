# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" NorthBound traffic generator """

import argparse
import logging
import nb_gen_utils
import os
import sys
import collections

FLOW_BODY_TEMPLATE = \
         """{
                "cookie": %d,
                "cookie_mask": 4294967295,
                "flow-name": "%s",
                "hard-timeout": %d,
                "id": "%s",
                "idle-timeout": %d,
                "installHw": true,
                "priority": 2,
                "strict": false,
                "table_id": 0,
                "match": {
                    "ipv4-destination": "%s/32",
                    "ethernet-match": {
                        "ethernet-type": {
                            "type": 2048
                        }
                    }
                },
                "instructions": {
                    "instruction": [
                        {
                            "apply-actions": {
                                "action": [
                                    {
                                        "drop-action": {},
                                        "order": 0
                                    }
                                ]
                            },
                            "order": 0
                        }
                    ]
                }               
            }"""




def flow_master(args):
    """Function executed by flow master thread.
    :param args: object containing ctrl_ip (controller IP),
    ctrl_port (controller RESTconf port), nflows (total number of flows to
    distribute), nworkers (number of worker threads to create),
    op_delay_ms (delay between thread operations (in milliseconds)),
    delete_flows_flag (whether to delete or not the added flows as part
    of the test), controller_restconf_user (controller RESTconf username),
    controller_restconf_password (controller RESTconf password)
    :returns: output_msg
    :rtype: str
    :type args: object of argparse.ArgumentParser()

    """
    print('entering main function...')
    flow_ops_params = collections.namedtuple('flow_ops_params', ['ctrl_ip',
        'ctrl_port', 'nflows', 'nworkers'])
    auth_token = collections.namedtuple('auth_token',
                                        ['controller_restconf_user',
                                         'controller_restconf_password'])

    controller_rest_auth_token = auth_token(args.restconf_user,
                                            args.restconf_password)

    flow_ops_params_set = flow_ops_params(args.ctrl_ip, args.ctrl_port,
                                          int(args.nflows), int(args.nworkers))
    delete_flows_flag = args.delete_flows_flag
    fpr = args.fpr
    op_delay_ms = int(args.op_delay_ms)
    flow_template = FLOW_BODY_TEMPLATE
    delete_url_template = 'http://' + flow_ops_params_set.ctrl_ip + ':' + \
        flow_ops_params_set.ctrl_port + \
        '/' + 'restconf/config/opendaylight-inventory:nodes/node/%s/' + \
        'table/0/flow/%d'
    add_url_template = 'http://' + flow_ops_params_set.ctrl_ip + ':' + \
        flow_ops_params_set.ctrl_port + \
        '/' + 'restconf/config/opendaylight-inventory:nodes/node/%s/' + \
        'table/0'
    node_names = nb_gen_utils.get_node_names(flow_ops_params_set.ctrl_ip,
                                             flow_ops_params_set.ctrl_port,
                                             controller_rest_auth_token)
    failed_flow_ops_del=0
    failed_flow_ops_add=0
    failed_flow_ops_total=0

    if delete_flows_flag == False:
        try:
            print('Main running add flows')
            # Calculate time needed for add flow operations
            failed_flow_ops_add = \
                nb_gen_utils.flows_transmission_run(flow_ops_params_set, op_delay_ms,
                                                node_names, add_url_template, flow_template,
                                                controller_rest_auth_token, fpr)
        except:

            failed_flow_ops_add = flow_ops_params_set.nflows
    else:

        # Calculate time needed for delete flow operations
        try:
            print('Main running delete flows')
            failed_flow_ops_del = \
                nb_gen_utils.flows_transmission_run(flow_ops_params_set, op_delay_ms,
                                                node_names, delete_url_template, 
                                                flow_template,
                                                controller_rest_auth_token, fpr,
                                                delete_flows_flag=True)
            
        except:
            print('exception in deletion occured')
            failed_flow_ops_del = flow_ops_params_set.nflows

    # sum up total failed flow operations
    failed_flow_ops_total = failed_flow_ops_add + failed_flow_ops_del

    output_msg = 'Total_failed_flows = {0}'.format(failed_flow_ops_total)

    return output_msg

if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--controller-ip',
                        required=True,
                        type=str,
                        dest='ctrl_ip',
                        action='store',
                        help=("The ip address of the controller. \n"
                              "This is a compulsory argument.\n"
                              "Example: --controller-ip='127.0.0.1'"))
    parser.add_argument('--controller-port',
                        required=True,
                        type=str,
                        dest='ctrl_port',
                        action='store',
                        help=("The port number of RESTCONF port of the "
                              "controller. \n"
                              "This is a compulsory argument.\n"
                              "Example: --controller-port='8181'"))
    parser.add_argument('--number-of-flows',
                        required=True,
                        type=str,
                        dest='nflows',
                        action='store',
                        help=("The total number of flow modifications. \n"
                              "This is a compulsory argument.\n"
                              "Example: --number-of-flows='1000'"))
    parser.add_argument('--number-of-workers',
                        required=True,
                        type=str,
                        dest='nworkers',
                        action='store',
                        help=("The total number of worker threads that will "
                              "be created. \n"
                              "This is a compulsory argument.\n"
                              "Example: --number-of-workers='10'"))
    parser.add_argument('--operation-delay',
                        required=True,
                        type=str,
                        dest='op_delay_ms',
                        action='store',
                        help=("The delay between each flow operation "
                              "(in ms). \n"
                              "This is a compulsory argument.\n"
                              "Example: --operation-delay='5'"))
    parser.add_argument('--delete-flows',
                        required=False,
                        dest='delete_flows_flag',
                        action='store_true',
                        default=False,
                        help=("Flag defining if we are going to have the "
                              "equivalent delete operations. \n"
                              "The default value is False. \n"
                              "Example: --delete-flag"))
    parser.add_argument('--restconf-user',
                        required=False,
                        type=str,
                        dest='restconf_user',
                        action='store',
                        default='admin',
                        help=("The controller's RESTCONF username. \n"
                              "The default value is 'admin'.\n"
                              "Example: --restconf-user='admin'"))
    parser.add_argument('--restconf-password',
                        required=False,
                        type=str,
                        dest='restconf_password',
                        action='store',
                        default='admin',
                        help=("The controller's RESTCONF password. \n"
                              "The default value is 'admin'.\n"
                              "Example: --restconf-password='admin'"))
    parser.add_argument('--fpr',
                        required=False,
                        type=int,
                        dest='fpr',
                        action='store',
                        default=1,
                        help=("Flows-per-Request - number of flows \n"
                        "(batch size) sent in each HTTP request"))
    parser.add_argument('--logging-level',
                        type=str,
                        dest='logging_level',
                        action='store',
                        default='DEBUG',
                        help="Setting the level of the logging messages."
                             "Can have one of the following values:\n"
                             "INFO\n"
                             "DEBUG (default)\n"
                             "ERROR")

    args = parser.parse_args()

    logging_format = '[%(asctime)s %(levelname)7s ] %(message)s'
    if args.logging_level == 'DEBUG':
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                        format=logging_format)
    elif args.logging_level == 'ERROR':
        logging.basicConfig(level=logging.ERROR, stream=sys.stdout,
                        format=logging_format)
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format=logging_format)

    abs_filename_path = os.path.abspath(__file__)
    abs_dir_path = os.path.dirname(abs_filename_path)
    os.chdir(abs_dir_path)

    result = flow_master(args)

    print(result)
