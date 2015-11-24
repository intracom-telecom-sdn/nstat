# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
from shutil import copyfile

"""Unittest Module for util/netutil.py."""

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
        cls.retries = 1
        cls.maxretries = 1
        cls.sleeptime = 2

        cls.remotemachineip = '127.0.0.1'
        cls.remotemachineport = 22
        cls.remotemachineusername = 'jenkins'
        cls.remotemachinepassword = 'jenkins'
        cls.remotemachinefilename = 'foofile.txt'
        cls.remotemachinefilenamefalse = 'foofile.mp3'
        cls.remotemachinepath = '/tmp'
        cls.remotemachinepath_false = '/test'
        cls.localmachinefolder = os.getcwd() + '/' + 'fooDir'
        cls.remotemachinefolder = cls.remotemachinepath + '/' + 'fooDir'

        createfilecommand = "touch" + " " + cls.remotemachinefilename
        subprocess.check_output(createfilecommand, shell=True)

        if not os.path.isdir(cls.localmachinefolder):
            os.mkdir(cls.localmachinefolder)
        exit
        while True:
            logging.info('[setup-netutil-test] Trying to connect to %s (%i/%i)',
                         cls.remotemachineip, cls.retries, cls.maxretries)
            response = os.system("ping -c 1 " + cls.remotemachineip)

            if response == 0:
                logging.info('[setup-netutil-test] remote machine: %s is up',
                             cls.remotemachineip)
                break
            else:
                logging.info('[setup-netutil-test] remote machine: %s, is '
                             'DOWN (%i/%i)', cls.remotemachineip, cls.retries,
                             cls.maxretries)
                cls.retries += 1
                time.sleep(cls.sleeptime)

            if cls.retries > cls.maxretries:
                logging.info('[setup-netutil-test] could not reach remote '
                             'machine: test cannot continue')
                return -1

    def test01_ssh_connect_or_return(self):
        """Testing ssh_connect_or_return() when entering a 'wrong' remote ip
        """
        logging.info('[netutil-test] remote address: {0} '.
                     format(self.remotemachineip))
        ipaddress_int = struct.unpack("!I",
                              socket.inet_aton(self.remotemachineip))[0]
        ipaddress_int += 1
        ipaddress_new = '192.168.64.15'
        logging.info('[netutil-test] remote address (altered): {0} '.
                     format(ipaddress_new))
        self.assertIsNone(util.netutil.ssh_connect_or_return(
                          ipaddress_new, self.remotemachineusername,
                          self.remotemachinepassword, self.maxretries))

    def test02_ssh_connect_or_return(self):
        """Testing ssh_connect_or_return() when entering a 'wrong' remote
        username
        """
        logging.info('[netutil-test] remote address: {0} '.
                     format(self.remotemachineip))
        logging.info('[netutil-test] remote user name: {0} '.
                     format(self.remotemachineusername))

        sizeofnewusername = 6
        chars = string.ascii_uppercase + string.digits
        username_new = ''.join(random.choice(chars)
                                     for _ in range(sizeofnewusername))
        logging.info('[netutil-test] remote username new: {0} '.
                     format(username_new))
        self.assertIsNone(util.netutil.ssh_connect_or_return(self.remotemachineip,
                          username_new, self.remotemachinepassword,
                          self.maxretries))

    def test03_ssh_connect_or_return(self):
        """Testing ssh_connect_or_return() when entering a 'wrong' remote password
        """
        chars = string.ascii_uppercase + string.digits
        sizeofnewpassword = 6
        password_new = ''.join(random.choice(chars)
                                     for _ in range(sizeofnewpassword))
        logging.info('[netutil-test] remote password new: {0} '.
                     format(password_new))
        self.assertIsNone(util.netutil.ssh_connect_or_return(self.remotemachineip,
                          self.remotemachineusername, password_new,
                          self.maxretries))

    def test04_isdir(self):
        """Testing isdir() when checking for an existing remote directory
        """
        transport_layer = paramiko.Transport((self.remotemachineip,
                                              self.remotemachineport))
        transport_layer.connect(username=self.remotemachineusername,
                                password=self.remotemachinepassword)
        sftp = paramiko.SFTPClient.from_transport(transport_layer)

        self.assertTrue(util.netutil.isdir(self.remotemachinepath, sftp))
        sftp.close()
        transport_layer.close()

    def test05_isdir(self):
        """Testing isdir() when checking for a non existing remote directory
        """
        transport_layer = paramiko.Transport((self.remotemachineip,
                                              self.remotemachineport))
        transport_layer.connect(username=self.remotemachineusername,
                                password=self.remotemachinepassword)
        sftp = paramiko.SFTPClient.from_transport(transport_layer)

        self.assertFalse(util.netutil.isdir(self.remotemachinepath_false, sftp))
        sftp.close()
        transport_layer.close()

    def test06_ssh_copy_file_to_target(self):
        """Testing ssh_copy_file_to_target(). Copying a local file to remote
        target and checking for its existence
        """
        local_file_path = os.getcwd() + '/' + self.remotemachinefilename
        remote_file_path = self.remotemachinepath  + '/' + \
                           self.remotemachinefilename


        util.netutil.ssh_copy_file_to_target(self.remotemachineip,
        self.remotemachineusername, self.remotemachinepassword, local_file_path,
        remote_file_path, self.remotemachineport)

        transport_layer = paramiko.Transport((self.remotemachineip,
                                              self.remotemachineport))
        transport_layer.connect(username=self.remotemachineusername,
                                password=self.remotemachinepassword)
        sftp = paramiko.SFTPClient.from_transport(transport_layer)

        # sftp.stat
        file_status = sftp.stat(remote_file_path)

        self.assertTrue(file_status)
        sftp.close()
        transport_layer.close()

    def test07_ssh_copy_file_to_target(self):
        """Testing ssh_copy_file_to_target(). Copying a local file to remote
        target (remotemachinefilename) and checking for the existence of a non
        existing file (remotemachinefilenamefalse). sftp.stat is expected to
        throw an exception
        """
        local_file_path = os.getcwd() + '/' + self.remotemachinefilename
        remote_file_path = self.remotemachinepath  + '/' + \
                           self.remotemachinefilename
        remote_file_path_false = self.remotemachinepath  + '/' + \
                                 self.remotemachinefilenamefalse

        util.netutil.ssh_copy_file_to_target(self.remotemachineip,
        self.remotemachineusername, self.remotemachinepassword, local_file_path,
        remote_file_path, self.remotemachineport)

        transport_layer = paramiko.Transport((self.remotemachineip,
                                              self.remotemachineport))
        transport_layer.connect(username=self.remotemachineusername,
                                password=self.remotemachinepassword)
        sftp = paramiko.SFTPClient.from_transport(transport_layer)

        file_status = sftp.stat(remote_file_path_false)

        self.assertTrue(file_status)
        sftp.close()
        transport_layer.close()

    def test08_copy_directory_to_target(self):
        """Testing copy_directory_to_target(). Copying a local empty directory
        to remote target and checking for its existence"""
        print(self.localmachinefolder)
        print(self.remotemachinefolder)

        util.netutil.copy_directory_to_target(self.remotemachineip,
        self.remotemachineusername, self.remotemachinepassword,
        self.localmachinefolder + '/', self.remotemachinefolder + '/',
        self.remotemachineport)

    def test09_copy_directory_to_target(self):
        """Testing copy_directory_to_target(). Copying a local NON empty
        directory to remote target and checking for its existence"""
        local_file_path = os.getcwd() + '/' + self.remotemachinefilename
        new_file_path = self.localmachinefolder + '/' + \
                        self.remotemachinefilename
        shutil.copy2(local_file_path, new_file_path)

        util.netutil.copy_directory_to_target(self.remotemachineip,
        self.remotemachineusername, self.remotemachinepassword,
        self.localmachinefolder, self.remotemachinefolder,
        self.remotemachineport)


    def test10_make_remote_file_executable(self):
        """Testing make_remote_file_executable(). Copying a local file to
        remote target, making it executable, testing if became executable"""

        pass

    def test11_create_remote_directory(self):
        """Testing create_remote_directory(). Creating a directory on the
        remote target, and using isdir to check for its existence"""

        pass

    def test11_remove_remote_directory(self):
        """Testing remove_remote_directory(). Creating a directory on the
        remote target using create_remote_directory, removing it using
        removed_remote_directory, and using isdir to check for its existence"""

        pass

    def test12_ssh_run_command(self):
        """ """
        pass

    def test13_ssh_delete_file_if_exists(self):
        """ Testing ssh_delete_file_if_exists. Copying localfilepath using
        ssh_copy_file_to_target(), and  ssh_delete_file_if_exists, checking file
        for its existence on the remote target"""
        pass


    @classmethod
    def tearDownClass(cls):
        """Kills the environment prepared at setUpClass
        """
        removefilecommand = "rm -rf" + " " + cls.remotemachinefilename
        subprocess.check_output(removefilecommand, shell=True)

        #removefoldercommand = "rm -rf" + " " + cls.localmachinefolder
        #subprocess.check_output(removefoldercommand, shell=True)

        del cls.remotemachinefilename
        del cls.remotemachineip
        del cls.remotemachinepassword
        del cls.remotemachineusername


if __name__ == '__main__':
    SUITE_NETUTILTEST = unittest.TestLoader().loadTestsFromTestCase(NetUtilTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE_NETUTILTEST)
