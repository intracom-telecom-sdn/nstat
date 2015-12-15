# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Unittest Module for util/netutil.py."""

import collections
import logging
import os
import paramiko
import random
import shutil
import socket
import string
import struct
import subprocess
import sys
import time
import unittest
import util.netutil

LOGGEROBJ = logging.getLogger()
LOGGEROBJ.level = logging.DEBUG

STREAMHANDLER = logging.StreamHandler(sys.stdout)
LOGGEROBJ.addHandler(STREAMHANDLER)

class NetUtilTest(unittest.TestCase):
    """Unitest class for testing methods within netutil.py
    Methods checked: testing file.py: ssh_connect_or_return, copy_to_target,
    make_remote_file_executable, ssh_run_command
    """

    @classmethod
    def setUpClass(cls):
        """Prepares the setup environment for testing methods
        ssh_connect_or_return, copy_to_target, make_remote_file_executable,
        ssh_run_command. The method assumes that a VM of certain ip,
        username, password is up. This method also creates a temporary file
        and a string with a location on the remote vm (need for the
        copy_to_target, make_remote_file_executable).
        """

        node_parameters = collections.namedtuple('ssh_connection',
        ['name', 'ip', 'ssh_port', 'username', 'password'])
        cls.remote_node = node_parameters('remote_node', '127.0.0.1', 22,
                                          'jenkins', 'jenkins')
        constants = collections.namedtuple('constants',
            ['retries','maxretries','sleeptime'])
        cls.constants_set = constants(1,1,2)
        file_paths = collections.namedtuple('file_paths',
            ['rem_node_file_name','rem_node_file_name_false','rem_node_path',
             'rem_node_path_false'])
        cls.file_paths_set = file_paths('foofile.txt','foofile.mp3','/tmp','/test')

        cls.localmachinefolder = os.getcwd() + '/' + 'fooDir'
        cls.remotemachinefolder = cls.file_paths_set.rem_node_path + '/' + 'fooDir'
        subprocess.check_output("touch" + " " +
                                cls.file_paths_set.rem_node_file_name_false,
                                shell=True)

    def test01_ssh_connect_or_return(self):
        """ssh_connect_or_return() false "remote ip" provided
        """
        logging.info('[netutil-test] remote address: {0} '.
                     format(self.remote_node.ip))
        ipaddress_int = struct.unpack("!I", socket.
                                      inet_aton(self.remote_node.ip))[0]
        ipaddress_int += 1
        ipaddress_new = '192.168.64.15'
        logging.info('[netutil-test] remote address (altered): {0} '.
                     format(ipaddress_new))
        self.assertIsNone(util.netutil.ssh_connect_or_return( ipaddress_new,
            self.remote_node.username, self.remote_node.password,
            self.constants_set.maxretries))

    def test02_ssh_connect_or_return(self):
        """ssh_connect_or_return() false "username" provided
        """
        logging.info('[netutil-test] remote address: {0} '.
                     format(self.remote_node.ip))
        logging.info('[netutil-test] remote user name: {0} '.
                     format(self.remote_node.username))
        sizeofnewusername = 6
        chars = string.ascii_uppercase + string.digits
        username_new = ''.join(random.choice(chars)
                                     for _ in range(sizeofnewusername))
        logging.info('[netutil-test] remote username new: {0} '.
                     format(username_new))
        self.assertIsNone(util.netutil.ssh_connect_or_return(
            self.remote_node.ip, username_new, self.remote_node.password,
            self.constants_set.maxretries))

    @classmethod
    def tearDownClass(cls):
        """Kills the environment prepared at setUpClass
        """
        #removefilecommand = "rm -rf" + " " + cls.remotemachinefilename
        #subprocess.check_output(removefilecommand, shell=True)
        pass


if __name__ == '__main__':
    SUITE_NETUTILTEST = unittest.TestLoader().loadTestsFromTestCase(NetUtilTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE_NETUTILTEST)
