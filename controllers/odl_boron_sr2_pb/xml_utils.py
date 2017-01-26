"""
This handler changes a xml parameter file and creates a new one according to \
    input string which is going to be updated and a new value string
"""

from lxml import etree
import os
import sys


def manipulate_xml(input_filename, output_filename,
                   string_to_find, target_value):
    """
    It gets a configuration (.xml in our case) file, defined by the \
        input_filename parameter and changes its contents defied by the \
        string_to_find parameter. The new values are defined in the \
        target_value parameter. The result is saved in a new file defined by \
        the output_file.

    :param input_filename: The configuration filepath we want to change.
    :param output_filename: The new configuration file, after changing the \
        original one.
    :param string_to_find: The string we want to change in the configuration \
        file.
    :param target_value: The new value to replace the string_to_find
    :type input_filename: str
    :type output_filename: str
    :type string_to_find: str
    :type target_value: str
    """

    if os.path.isfile(input_filename):
        doc = etree.parse(input_filename)
        #go inside snapshot
        for  elt in doc.getiterator():
            if string_to_find in elt.tag:
                elt.text = target_value
        outFile = open(output_filename, 'wb')
        doc.write(outFile)
    else:
        sys.exit(1)
