# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Unittest Module for util/cpu.py."""

import unittest
import util.cpu


class CpuComputeCpuShares(unittest.TestCase):
    """Unittest class testing the different functionalities of
    compute_cpu_shares() function in module util/cpu.py.
    """

    def test01_compute_cpu_shares(self):
        """Checks the compute_cpu_shares() function of
        util/cpu.py. It checks the equality of the result of a valid input.
        """

        self.assertTupleEqual(([0, 1, 2], [3]),
                              util.cpu.compute_cpu_shares([75, 25], 4),
                              'Testing cpu share for ([75,25], 4)')

    def test02_compute_cpu_shares(self):
        """Checks the compute_cpu_shares() function of
        util/cpu.py. It checks the equality of the result of a valid input.
        """

        self.assertTupleEqual(([0, 1, 2, 3, 4, 5], [6, 7]),
                              util.cpu.compute_cpu_shares([75, 25], 8),
                              'Testing cpu share for ([75,25], 8)')

    def test03_compute_cpu_shares(self):
        """Checks the compute_cpu_shares() function of
        util/cpu.py. It checks the equality of the result of a valid input.
        """

        self.assertTupleEqual(([0, 1, 2, 3, 4, 5, 6, 7],
                               [0, 1, 2, 3, 4, 5, 6, 7]),
                              util.cpu.compute_cpu_shares([100, 100], 8),
                              'Testing cpu share for ([100,100], 8)')

    def test04_compute_cpu_shares(self):
        """Checks the compute_cpu_shares() function of util/cpu.py.
        It checks the equality of the result of a valid input.
        """

        self.assertTupleEqual(([0, 1, 2, 3, 4, 5, 6, 7],
                               [0, 1, 2, 3, 4, 5, 6, 7]),
                              util.cpu.compute_cpu_shares([0, 0], 8),
                              'Testing cpu share for ([0,0], 8)')

    def test05_compute_cpu_shares(self):
        """Checks the compute_cpu_shares() function of util/cpu.py.
        It checks the equality of the result of a invalid input.
        It checks if the appropriate ValueError exception is raised.
        """
        with self.assertRaises(ValueError):
            util.cpu.compute_cpu_shares([75, 25], 1)

    def test06_compute_cpu_shares(self):
        """Checks the compute_cpu_shares() function of util/cpu.py.
        It checks the equality of the result of a invalid input.
        It checks if the appropriate ValueError exception is raised.
        """
        with self.assertRaises(ValueError):
            util.cpu.compute_cpu_shares([75, 125], 4)

    def test07_compute_cpu_shares(self):
        """Checks the compute_cpu_shares() function of util/cpu.py.
        It checks the equality of the result of a invalid input.
        It checks if the appropriate ValueError exception is raised.
        """
        with self.assertRaises(ValueError):
            util.cpu.compute_cpu_shares([75, 25], 2)

if __name__ == '__main__':
    SUITE_CPU_TEST = \
    unittest.TestLoader().loadTestsFromTestCase(CpuComputeCpuShares)
    unittest.TextTestRunner(verbosity=2).run(SUITE_CPU_TEST)
