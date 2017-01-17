#! /usr/bin/env python3.4

"""
Handler changing the rate of statistics collection from the topology switches
"""

import xml_utils
import sys
import os

CONTROLLER_DIR_NAME = 'distribution-karaf-0.3.3-Lithium-SR3'

def change_stats_period():
    """
    Takes as command line argument the new interval of statistics period we \
        want to set in the configuration file of the controller and writes it \
        in this file.
    """

    string_to_find = 'min-request-net-monitor-interval'
    input_file = os.path.sep.join([os.path.dirname(os.path.realpath(__file__)),
                                   CONTROLLER_DIR_NAME, 'etc', 'opendaylight',
                                   'karaf', '30-statistics-manager.xml'])
    xml_utils.manipulate_xml(input_file, input_file, string_to_find,
                             str(int(sys.argv[1])))


if __name__ == '__main__':
    change_stats_period()
