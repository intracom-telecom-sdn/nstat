__author__ = "Jan Medved"
__copyright__ = "Copyright(c) 2014, Cisco Systems, Inc."
__license__ = "New-style BSD"
__email__ = "jmedved@cisco.com"

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""
Reusable classes or functions for processes that are flow manipulation related
url: https://wiki.opendaylight.org/view/CrossProject:Integration_Group:Performance_Tests
Acknowledgement: Jan Medved, jmedved@cisco.com, Cisco Systems, Inc.
"""

import requests
import re
import json
import logging


class FlowProcessor(object):
    """
    Helper object used to add and remove flows based on predefined templates.
    """

    def __init__(self, flow_template, url_template, auth_token):
        """
        :param flow_template: template of the actual json call representing
        a flow
        :param url_template: template for the url used for each flow
        :param auth_token: restconf authorization token (username/password tuple)
        :type flow_template: str
        :type url_template: str
        :type auth_token: tuple<str>
        """

        self.putheaders = {'content-type': 'application/json'}
        self.getheaders = {'Accept': 'application/json'}
        self.flow_template = flow_template
        self.url_template = url_template
        self.session = requests.Session()
        self.session.trust_env = False
        self.auth_token = auth_token
        self.flow_template = """{"flow": [%s]}"""

    def add_flow(self, flow_data_body, node_id):
        """
        Adds a flow to the specified node

        :param node_id: ID of the node to which we will add the flow
        :param ip_dest: IP address to populate the destination IP field of the
        flow template
        :returns: status code for the http call issued
        :rtype: int
        :type node_id: int
        :type ip_dest: str
        """

        # Disable logging during performing requests
        logging.disable(logging.CRITICAL)
        flow_data = self.flow_template % (flow_data_body)
        flow_url = self.url_template % (node_id)
        try:
            request = self.session.post(flow_url, data=flow_data,
                                       headers=self.putheaders, stream=False,
                                       auth=self.auth_token)
            return request.status_code
        except:
            return -1
        finally:
            # Enable logging after performing requests
            logging.disable(logging.NOTSET)

    def remove_flow(self, flow_id, node_id):
        """
        Removes a flow from the specified node

        :param flow_id: ID of the flow to remove
        :param node_id: ID of the node from which the flow will be removed
        :returns: status code for the http call issued
        :rtype: int
        :type flow_id: int
        :type node_id: int
        """

        # Disable logging during performing requests
        logging.disable(logging.CRITICAL)
        flow_url = self.url_template % (node_id, flow_id)
        try:
            request = self.session.delete(flow_url, headers=self.getheaders,
                                          auth=self.auth_token)
            return request.status_code
        except:
            return -1
        finally:
            # Enable logging after performing requests
            logging.disable(logging.NOTSET)


class FlowExplorer(object):
    """
    Object used to explore controller inventory flows, using the NB REST
    interface.
    """

    def __init__(self, controller_ip, restconf_port, datastore, auth_token):
        """
        :param controller_ip: controller IP address
        :param restconf_port: controller RESTconf port number
        :param datastore: type datastore elements to retrieve from operational
        datastore.
        :param auth_token: restconf authorization token (username/password tuple)
        :type controller_ip: str
        :type restconf_port: int
        :type datastore: str
        :type auth_token: tuple<str>
        """
        self.inventory_stats_url = \
            'http://{0}:{1}/restconf/{2}/opendaylight-inventory:nodes'.format(
             controller_ip, restconf_port, datastore)
        self.found_flows = 0
        self.active_flows = 0
        self.table_stats_unavailable = 0
        self.table_stats_fails = []
        self.getheaders = {'Accept': 'application/json'}
        self.auth_token = auth_token

    def get_inventory_flows_stats(self):
        """
        Collects and prints statistics information about all installed flows
        for all the nodes of the topology
        """

        self.found_flows = 0
        self.active_flows = 0
        self.table_stats_unavailable = 0
        self.table_stats_fails = []

        # Disable logging during performing requests
        logging.disable(logging.CRITICAL)
        s = requests.Session()
        s.trust_env = False
        try:
            req = s.get(self.inventory_stats_url,
                        headers=self.getheaders,
                        stream=False,
                        auth=self.auth_token)
            str_response = req.content.decode('utf-8')
        except:
            self.active_flows = 0
            self.found_flows = 0
            return -1
        finally:
            # Enable logging after performing requests
            logging.disable(logging.NOTSET)

        if req.status_code == 200:
            try:
                self.nodes = json.loads(str_response)['nodes']['node']
                switches = []
                for node in self.nodes:
                    if re.search('openflow', node['id']) is not None:
                        switches.append(node)

                switches = sorted(
                    switches,
                    key=lambda k: int(
                        re.findall(
                            '\d+',
                            k['id'])[0]))

                for switch in switches:
                    try:
                        tables = switch['flow-node-inventory:table']

                        for table in tables:
                            try:
                                stats = table['opendaylight-flow-table-statistics:flow-table-statistics']
                                self.active_flows = int(stats['active-flows'])
                            except KeyError:
                                self.table_stats_unavailable += 1

                            try:
                                self.found_flows += len(table['flow'])
                            except KeyError:
                                pass

                        if self.table_stats_unavailable > 0:
                            self.table_stats_fails.append(switch['id'])
                    except KeyError:
                            logging.error('Data for tables not available.')

            except KeyError:
                logging.error('Could not retrieve inventory, response not in '
                              'JSON format')
        else:
            logging.error('Could not retrieve inventory, HTTP error {0}'.
                          format(req.status_code))
        s.close()

