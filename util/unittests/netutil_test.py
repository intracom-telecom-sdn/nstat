# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Unittest Module for util/netutil.py."""

import logging
import os
import random
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

    def setUp(self):
        """Prepares the setup environment for testing methods
        ssh_connect_or_return, copy_to_target, make_remote_file_executable,
        ssh_run_command. The method assumes that a VM of certain ip,
        username, password is up. This method also creates a temporary file
        and a string with a location on the remote vm (need for the
        copy_to_target, make_remote_file_executable).
        """
        self.retries = 1
        self.maxretries = 1
        self.sleeptime = 2

        self.remotemachineip = '127.0.0.1'
        self.remotemachineusername = 'jenkins'
        self.remotemachinepassword = 'jenkins'
        self.remotemachinefilename = 'foofile.txt'
        commandtorun = "touch" + " " + self.remotemachinefilename
        subprocess.check_output(commandtorun, shell=True)

        while True:
            logging.info('[setup-netutil-test] Trying to connect to %s (%i/%i)',
                         self.remotemachineip, self.retries, self.maxretries)
            response = os.system("ping -c 1 " + self.remotemachineip)

            if response == 0:
                logging.info('[setup-netutil-test] remote machine: %s is up',
                             self.remotemachineip)
                break
            else:
                logging.info('[setup-netutil-test] remote machine: %s, is '
                             'DOWN (%i/%i)', self.remotemachineip, self.retries,
                             self.maxretries)
                self.retries += 1
                time.sleep(self.sleeptime)

            if self.retries > self.maxretries:
                logging.info('[setup-netutil-test] could not reach remote '
                             'machine: test cannot continue')
                return -1


    def tearDown(self):
        """Kills the environment prepared at method: setUp
        """
        commandtorun = "rm -rf" + " " + self.remotemachinefilename
        subprocess.check_output(commandtorun, shell=True)

        del self.remotemachinefilename
        del self.remotemachineip
        del self.remotemachinepassword
        del self.remotemachineusername

    def test01_ssh_connect_or_return(self):
        """Testing ssh_connect_or_return() when entering a 'wrong' remote ip
        """
        tst01_username = self.remotemachineusername
        tst01_password = self.remotemachinepassword
        tst01_maxtries = self.maxretries
        tst01_ipaddress = self.remotemachineip
        logging.info('[netutil-test] remote address: {0} '.
                     format(tst01_ipaddress))
        tst01_ipaddress_int = struct.unpack("!I",
                                            socket.
                                            inet_aton(tst01_ipaddress))[0]
        tst01_ipaddress_int += 1
        #tst01_ipaddress_new = socket.inet_ntoa(struct.pack("!I",
        #                                                   tst01_ipaddress_int))
        tst01_ipaddress_new = '192.168.64.15'
        logging.info('[netutil-test] remote address (altered): {0} '.
                     format(tst01_ipaddress_new))
        #print('setup environment address:', format(tst01_ipaddress))
        #print('new wrong environment address:', format(tst01_ipaddress_new))
        self.assertTrue(util.netutil.ssh_connect_or_return(tst01_ipaddress_new,
                        tst01_username, tst01_password, tst01_maxtries))

    def test02_ssh_connect_or_return(self):
        """Testing ssh_connect_or_return() when entering a 'wrong' remote username
        """
        tst02_username = self.remotemachineusername
        tst02_password = self.remotemachinepassword
        tst02_maxtries = self.maxretries
        tst02_ipaddress = self.remotemachineip
        logging.info('[netutil-test] remote address: {0} '.
                     format(tst02_ipaddress))
        logging.info('[netutil-test] remote user name: {0} '.
                     format(tst02_username))
        #generate random username and check connectivity
        sizeofusernamenew = 6
        chars = string.ascii_uppercase + string.digits
        tst02_username_new = ''.join(random.choice(chars)
                                     for _ in range(sizeofusernamenew))
        logging.info('[netutil-test] remote username new: {0} '.
                     format(tst02_username_new))
        self.assertTrue(util.netutil.ssh_connect_or_return(tst02_ipaddress,
                        tst02_username_new, tst02_password, tst02_maxtries))

if __name__ == '__main__':
    SUITE_NETUTILTEST = unittest.TestLoader().loadTestsFromTestCase(NetUtilTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE_NETUTILTEST)
