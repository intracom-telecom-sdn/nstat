#! /usr/bin/env python3.4
import emulators.nb_generator.flow_utils
import logging
import sys

def get_oper_flows():
    """Query number of flows registered in ODL operational DS

    :returns: number of flows found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    """

    ip = str(int(sys.argv[1]))
    port = int(sys.argv[2])
    username = str(int(sys.argv[3]))
    password = str(int(sys.argv[4]))

    odl_flow_inventory = emulators.nb_generator.flow_utils.FlowExplorer(ip,
                                                                        port,
                                                                        'operational',
                                                                        username,
                                                                        password)
    odl_flow_inventory.get_inventory_flow()
    logging.debug('[get_oper_flows] Discovered {0} flows at inventory'.format(odl_flow_inventory.found_flows))
    return odl_flow_inventory.found_flows

if __name__ == '__main__':
    get_oper_flows()