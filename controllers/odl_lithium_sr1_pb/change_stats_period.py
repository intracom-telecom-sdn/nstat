#! /usr/bin/env python3.4

from lxml import etree
import sys
import os


def manipulate_xml(input_filename, output_filename,
                   string_to_find, target_value):
    """It gets a configuration (.xml in our case) file, defined by the
    input_filename parameter and changes its contents defied by the
    string_to_find parameter. The new values are defined in the target_value
    parameter. The result is saved in a new file defined by the output_file.

    :param input_filename: The configuration filepath we want to change.
    :param output_filename: The new configuration file, after changing the
    original one.
    :param string_to_find: The string we want to change in the configuration
    file.
    :param target_value: The new value to replace the string_to_find
    :type input_filename: str
    :type output_filename: str
    :type string_to_find: str
    :type target_value: str
    """

    doc = etree.parse(input_filename)
    #go inside snapshot
    for  elt in doc.getiterator():
        if string_to_find in elt.tag:
            elt.text = target_value
    outFile = open(output_filename, 'wb')
    doc.write(outFile)

def change_stats_period_main():
    """Takes as command line argument the new interval of statistics period we
    want to set in the configuration file of the controller and writes it in
    this file.
    """

    string_to_find = 'min-request-net-monitor-interval'
    input_file = os.path.dirname(os.path.realpath(__file__)) + \
        '/distribution-karaf-0.3.1-Lithium-SR1/etc/opendaylight/karaf/30-statistics-manager.xml'
    manipulate_xml(input_file, input_file, string_to_find,
                   str(int(sys.argv[1])))

if __name__ == '__main__':
    change_stats_period_main()