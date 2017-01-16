# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Unittest Module for util/numeric.py."""

import unittest
import util.numeric

class NumericTonum(unittest.TestCase):
    """
    Unittest class to test the different functionalities of tonum()
    function in module util/numeric.py. Tests the cases of
    - impossible numeric casting
    - integer numeric casting
    - float numeric casting
    """

    def test01_tonum(self):
        """
        Checks the tonum() method of util/numeric.py.
        It checks the case of impossible numeric casting.
        """
        self.assertEqual('Impossible cast', util.numeric.tonum('rty'),
                         'Testing impossible casting case')

    def test02_tonum(self):
        """
        Checks the tonum() method of util/numeric.py.
        It checks the case of integer numeric casting.
        """
        self.assertEqual(10, util.numeric.tonum('10'),
                         'Testing casting to integer')

    def test03_tonum(self):
        """
        Checks the tonum() method of util/numeric.py.
        It checks the case of float numeric casting.
        """
        self.assertEqual(10.12334, util.numeric.tonum('10.12334'),
                         'Testing casting to float')

if __name__ == '__main__':
    SUITE_NUMERICTONUM = \
    unittest.TestLoader().loadTestsFromTestCase(NumericTonum)
    unittest.TextTestRunner(verbosity=2).run(SUITE_NUMERICTONUM)

