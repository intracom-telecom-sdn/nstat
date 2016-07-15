# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Unittest Module for util/customsubprocess.py."""

import unittest
import util.customsubprocess
import Queue


class CustomSubprocessCheckOutputStream(unittest.TestCase):
    """Unittest class that checks the functionality of
    check_output_streaming() function of util/customsubprocess.py module. It
    tests.
    - using the function with 1 input argument
    - using the function with 2 input arguments
    - using the function with 3 input arguments
    - The contents of the Queue structure, that is passed as argument,
    after the execution of the function
    """

    def setUp(self):
        """Creates a Queue data structure that is
        necessary for  testing the functions of util/customsubprocess.py
        module.
        """

        self.testing_queue = Queue.Queue()

    def test01_check_output_streaming(self):
        """Tests the check_output_streaming() method of
        util/customsubprocess.py module, when using it with 1 input argument.
        """

        self.assertEqual(0,
                         util.customsubprocess.check_output_streaming('ls'),
                         'Testing check_output_streaming test1')

    def test02_check_output_streaming(self):
        """Tests the check_output_streaming() method
        of util/customsubprocess.py module, when using it with 2 input
        arguments
        """

        self.assertEqual(0,
                         util.customsubprocess.check_output_streaming('ls',
                                                                      'test'),
                         'Testing check_output_streaming test2')

    def test03_check_output_streaming(self):
        """Tests the check_output_streaming() method
        of util/customsubprocess.py module, when using it with 3 input
        arguments
        """

        self.assertEqual(0,
                         util.customsubprocess.
                         check_output_streaming('ls',
                                                'test', self.testing_queue),
                         'Testing check_output_streaming test3')

    def test04_check_output_streaming(self):
        """Tests the contents of the Queue structure used from
        check_output_streaming() method of util/customsubprocess.py module.
        """

        util.customsubprocess.check_output_streaming('ls', 'test',
                                                     self.testing_queue)
        self.assertFalse(self.testing_queue.empty(),
                         ('Checking if testing_queue is empty. '
                          'This test fails if the queue is empty.'))

    def tearDown(self):
        """Deletes the Queue data structure, created from setUp()
        method necessary for testing the functions of util/customsubprocess.py
        module.
        """

        del self.testing_queue

if __name__ == '__main__':
    SUITE_CUSTOM_SUBPROCESS_TEST = unittest.TestLoader().\
    loadTestsFromTestCase(CustomSubprocessCheckOutputStream)
    unittest.TextTestRunner(verbosity=2).run(SUITE_CUSTOM_SUBPROCESS_TEST)


