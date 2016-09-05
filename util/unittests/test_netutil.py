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
LOGGEROBJ.level = logging.INFO

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
                                          'konpap', 'konpap')
        constants = collections.namedtuple('constants',
            ['maxretries','sleeptime'])
        cls.constants_set = constants(5,2)
        file_paths = collections.namedtuple('file_paths',
            ['loc_node_file_name','rem_node_file_name_false','rem_node_path',
             'rem_node_path_create'])
        cls.file_paths_set = file_paths('foofile.txt','foofile.mp3','/tmp','/test')

        cls.localnodefilepath = os.getcwd() + '/' + 'fooDir/'
        cls.remotenodefolderpath = cls.file_paths_set.rem_node_path
        subprocess.check_output("touch" + " " +
                                cls.file_paths_set.loc_node_file_name,
                                shell=True)
        if not os.path.isdir(cls.localnodefilepath):
            os.mkdir(cls.localnodefilepath)
        retries = 1
        while True:
            logging.info('[setup-netutil-test] trying to connect to %s (%i/%i)',
                         cls.remote_node.ip, retries,
                         cls.constants_set.maxretries)
            response = os.system("ping -c 1 " + cls.remote_node.ip)

            if response == 0:
                logging.info('remote machine: %s is up', cls.remote_node.ip)
                break
            else:
                logging.info('remote machine: %s, is '
                    'DOWN (%i/%i)', cls.remote_node.ip,
                    retries, cls.constants_set.maxretries)
                retries += 1
                time.sleep(cls.constants_set.sleeptime)

            if retries > cls.constants_set.maxretries:
                logging.info('could not reach remote node: test cannot continue')

                return -1
    def test01_ssh_connection_open(self):
        """ssh_connection_open() false "remote ip" provided
        """
        logging.info('[netutil-test] remote address: {0} '.
                     format(self.remote_node.ip))
        (sftp, transport_layer) = \
            util.netutil.ssh_connection_open(self.remote_node)
        self.assertIsNotNone(sftp)
        util.netutil.ssh_connection_close(sftp, transport_layer)

    def test02_ssh_connect_or_return(self):
        """ssh_connect_or_return() check returned ssh object
        """
        logging.info('[netutil-test] remote address: {0} '.
                     format(self.remote_node.ip))
        self.assertIsNotNone(util.netutil.ssh_connect_or_return(
             self.remote_node, self.constants_set.maxretries))

    def test03_isdir(self):
        """testing isdir() with /tmp on localhost
        """
        (sftp, transport_layer) = \
            util.netutil.ssh_connection_open(self.remote_node)
        logging.info('[netutil-test] opened connection with: {0} - {1} '.
                     format(self.remote_node.ip, self.remote_node.username))
        self.assertTrue(util.netutil.isdir(self.file_paths_set.rem_node_path,
                                           sftp))
        util.netutil.ssh_connection_close(sftp, transport_layer)

    def test04_ssh_copy_file_to_target(self):
        """ssh_copy_file_to_target() copying a local file to remote target
        """
        subprocess.check_output("touch" + " " + 'fooDir/' +
                                self.file_paths_set.loc_node_file_name,
                                shell=True)
        localfile  = self.localnodefilepath +  \
            self.file_paths_set.loc_node_file_name
        remotefile = self.remotenodefolderpath + '/' + \
            self.file_paths_set.loc_node_file_name
        logging.info('copying from file: {0} from local path - to remote node {1} '.
                     format(localfile, remotefile))

    def test05_copy_dir_local_to_remote(self):
        """copy_dir_local_to_remote(). copying a local directory to remote node
         """
        util.netutil.copy_dir_local_to_remote(self.remote_node,self.localnodefilepath,
            self.remotenodefolderpath)
        (sftp, transport_layer) = \
        util.netutil.ssh_connection_open(self.remote_node)
        self.assertTrue(util.netutil.isdir(self.file_paths_set.rem_node_path,
                                           sftp))
    def test06_create_dir_remote(self):
        """create_dir_remote(). creating directory to remote node
        """
        remote_dir_create = self.file_paths_set.rem_node_path + \
            self.file_paths_set.rem_node_path_create
        logging.info('creating directory: {0} at remote node {1} '.
                     format(remote_dir_create, self.remote_node.ip))
        util.netutil.create_dir_remote(self.remote_node,
            remote_dir_create)

    def test07_ssh_connect_or_return2(self):
        """ssh_connect_or_return2() check returned ssh object
        """
        logging.info('[netutil-test] remote address: {0} '.
                     format(self.remote_node.ip))
        self.assertIsNotNone(util.netutil.ssh_connect_or_return2(
             self.remote_node.ip, self.remote_node.ssh_port, self.remote_node.username, self.remote_node.password, self.constants_set.maxretries))

        pass
    @classmethod
    def tearDownClass(cls):
        """cleans setUpClass environment
        """
        subprocess.check_output("rm -rf" + " " + "foo*", shell=True)


if __name__ == '__main__':
    SUITE_NETUTILTEST = unittest.TestLoader().loadTestsFromTestCase(NetUtilTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE_NETUTILTEST)
