#! /usr/bin/env python3.4

"""
Handler disabling the percistence mode in the configuration of the controller.
"""

import sys
import os

CONTROLLER_DIR_NAME = 'distribution-karaf-0.4.0-Beryllium'


def change_persistence():
    """
    Change the persistence attribute to false. The controller will not backup \
        datastore on the disk.
    """

    string_to_find = '#persistent=true'
    string_to_replace = 'persistent=false'
    filedata = ''
    input_file = os.path.sep.join([os.path.dirname(os.path.realpath(__file__)),
                                   CONTROLLER_DIR_NAME, 'etc',
                                   'org.opendaylight.controller.cluster.datastore.cfg'])
    with open(input_file, 'rb') as f:
        filedata = f.read().decode('utf-8')
    if filedata == '':
        print('[change_persistent] Fail to read file')
        sys.exit(1)
    filedata = filedata.replace(string_to_find, string_to_replace)
    try:
        with open(input_file, 'wb') as f:
            f.write(filedata.encode('utf-8'))
    except:
        print('[change_persistent] Fail to write file')
        sys.exit(1)

if __name__ == '__main__':
    change_persistence()
