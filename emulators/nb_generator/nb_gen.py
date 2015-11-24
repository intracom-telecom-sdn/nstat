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
import time

F_TEMP = """{
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


def flow_master(ctrl_ip, ctrl_port, nflows, nworkers, op_delay_ms, delete_flag,
                discovery_deadline_ms, controller_restconf_user,
                controller_restconf_password):
    """Function executed by flow master thread.

    :param ctrl_ip: controller IP
    :param ctrl_port: controller RESTconf port
    :param nflows: total number of flows to distribute
    :param nworkers: number of worker threads to create
    :param op_delay_ms: delay between thread operations (in milliseconds)
    :param delete_flag: whether to delete or not the added flows as part of the
    test
    :param discovery_deadline_ms: deadline for flow discovery (in milliseconds)
    :param controller_restconf_user: Controller RESTconf username
    :param controller_restconf_password: Controller RESTconf username
    :type ctrl_ip: str
    :type ctrl_port: str
    :type nflows: int
    :type nworkers: int
    :type op_delay_ms: int
    :type delete_flag: bool
    :type discovery_deadline_ms: int
    :type controller_restconf_user: str
    :type controller_restconf_password: str
    """

    flow_template = F_TEMP
    results = []
    failed_flow_ops = 0
    auth_token = (controller_restconf_user, controller_restconf_password)
    node_names = nb_gen_utils.get_node_names(ctrl_ip, ctrl_port, auth_token)

    url_template = 'http://' + ctrl_ip + ':' + ctrl_port + \
        '/' + 'restconf/config/opendaylight-inventory:nodes/node/%s/' + \
        'table/0/flow/%d'

    #Calculation addition time
    nb_gen_utils.flow_operations_calc_time(ctrl_ip, ctrl_port, nflows,
                                               nworkers, op_delay_ms,
                                               discovery_deadline_ms,
                                               controller_restconf_user,
                                               controller_restconf_password,
                                               delete_flag=False)


    #Calculation deletion time if delete_flag TRUE
    if delete_flag:
        nb_gen_utils.flow_operations_calc_time(ctrl_ip, ctrl_port, nflows,
                                               nworkers, op_delay_ms,
                                               discovery_deadline_ms,
                                               controller_restconf_user,
                                               controller_restconf_password,
                                               delete_flag=False)
    results.append(failed_flow_ops)


    output_msg = 'Results:\n'
    output_msg += 'Add_flows_transmission_time/Add_flows_time/'
    if len(results) == 5:
        output_msg += 'Delete_flows_transmission_time/Delete_flows_time/'
    output_msg += 'Total_failed_flows = '
    output_msg += '/'.join(str(result) for result in results)
    output_msg += '\nAll times are in seconds.'
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
                        dest='delete_flag',
                        action='store_true',
                        default=False,
                        help=("Flag defining if we are going to have the "
                              "equivalent delete operations. \n"
                              "The default value is False. \n"
                              "Example: --delete-flag"))
    parser.add_argument('--discovery-deadline',
                        required=False,
                        type=str,
                        dest='discovery_deadline_ms',
                        action='store',
                        default='240000',
                        help=("The deadline to discover switches (in ms). \n"
                              "The default value is '240000'.\n"
                              "Example: --discovery-deadline='240000'"))
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

    result = flow_master(args.ctrl_ip, args.ctrl_port, int(args.nflows),
        int(args.nworkers), int(args.op_delay_ms),
        args.delete_flag, int(args.discovery_deadline_ms),
        args.restconf_user, args.restconf_password)

    print(result)
