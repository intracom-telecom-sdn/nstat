# Copyright (c) 2015 Intracom socket_obj.A. Telecom Solutions.
#All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Unittest Module for util/process.py."""

import logging
import multiprocessing
import os
import socket
import subprocess
import sys
import unittest
import util.process

LOGGER = logging.getLogger()
LOGGER.level = logging.INFO
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(STREAM_HANDLER)


def server_init(listen_port):
    """The helper method start a server process that listens to a predefined
    port

    :param listen_port: The port number where the server process is listening
    :returns A socket object that will be passed inside the server process
    (see function server_thread()).
    :rtype: socket.socket()
    """
    try:
        # Create a socket object
        socket_obj = socket.socket()
        # Get local machine name
        host = socket.gethostname()
        # Reserve a port for your service.
        port = listen_port
        # Bind to the port
        socket_obj.bind((host, port))
        # Now wait for client connection.
        socket_obj.listen(5)
        return socket_obj
    except:
        logging.getLogger().info('Could not start a listening server on '
                                 'port {0} exiting...'.format(listen_port))
        exit(1)


def server_thread(socket_obj):
    """Runs as a separate child process. It takes as argument a
    socket object.
    """
    # Establish connection with client.
    conn, addr = socket_obj.accept()
    logging.getLogger().info('Got connection from '
                             '{0}'.format(addr))

class ProcessTestAllFunctions(unittest.TestCase):
    """This Unittest class tests the different functionalities of the module
    util/process.py.
    """

    @classmethod
    def setUpClass(cls):
        """Initializes the testing environment parameters. Starts
        the server process
        """
        cls.LISTEN_PORT = 65535
        cls.SERVER_PID = ''
        cls.invalid_port = 'this is not a port'
        cls.invalid_process = 'this is not a process'
        cls.port_not_owned = ''
        # Initialize and start server process that mocks the controller
        cls.s = server_init(cls.LISTEN_PORT)
        cls.srv = multiprocessing.Process(target=server_thread, args=(cls.s,))
        cls.srv.start()
        # Finding an not owned port
        for line in subprocess.check_output('netstat -tulpn --numeric-ports',
                                            shell=True,
                                            universal_newlines=True).\
                                            split('\n'):
            try:
                if_condition1 = line.split()[-1] == '-'
                if_condition2 = line.split()[3].split(':')[-1] != '*'
                if_condition3 = cls.port_not_owned == ''
                if if_condition1 and if_condition2 and if_condition3:
                    cls.port_not_owned = \
                    str(line.split()[3].split(':')[-1])
            except:
                continue
        if cls.port_not_owned == '':
            logging.getLogger().info('Could not find a process that belongs '
                                     'to another user. Will exit...')
            exit(1)
        cls.SERVER_PID = os.getpid()
        logging.getLogger().info('SERVER PID: %d', cls.SERVER_PID)
        logging.getLogger().info('NOT OWNED PORT: %s', cls.port_not_owned)

    def test01_getpid_listeningonport(self):
        """Checks the getpid_listeningonport() function of
        util/process.py module. Checks the equality between the known process
        id of the initializes server, with the one returned from the function.
        """
        self.assertEqual(self.SERVER_PID,
                         util.process.\
                         getpid_listeningonport(self.LISTEN_PORT),
                         'Testing the returned PID')

    def test02_getpid_listeningonport(self):
        """Checks the getpid_listeningonport() function of
        util/process.py module. In this scenario we check the result in case
        we give as input to the function, a port number on which a process
        that the user not owns is listening.
        """
        self.assertEqual(0,
                         util.process.\
                         getpid_listeningonport(self.port_not_owned),
                         'Testing when port is not owned')

    def test03_getpid_listeningonport(self):
        """Checks the getpid_listeningonport() function of
        util/process.py module. In this scenario we check the result in case
        we give as input to the function something that is not a port number.
        """
        self.assertEqual(-1,
                         util.process.\
                         getpid_listeningonport(self.invalid_process),
                         'Testing with an invalid port ')


    def test01_is_process_running(self):
        """Checks the is_process_running() function of
        util/process.py module. In this scenario we check the result in case
        we give as input to the function a valid process id.
        """
        self.assertTrue(util.process.is_process_running(self.SERVER_PID),
                        'Testing true case for a valid process id')

    def test02_is_process_running(self):
        """Checks the is_process_running() function of
        util/process.py module. In this scenario we check the result in case
        we give as input to the function a invalid process id.
        """
        self.assertFalse(util.process.is_process_running(self.invalid_process),
                         'Testing false case for invalid process id')

    def test03_is_process_running(self):
        """Checks the is_process_running() function of
        util/process.py module. In this scenario we check the result in case
        we give as input to the function a invalid process id.
        """
        self.assertTrue(util.process.is_process_running(1),
                         'Testing most privileged process id 1')

    @classmethod
    def tearDownClass(cls):
        """Cleans the testing environment parameters. Stops the
        server process we started
        """
        cls.srv.terminate()

if __name__ == '__main__':
    SUITE_PROCESSTESTALLFUNCTIONS = unittest.TestLoader().\
    loadTestsFromTestCase(ProcessTestAllFunctions)
    unittest.TextTestRunner(verbosity=2).run(SUITE_PROCESSTESTALLFUNCTIONS)

