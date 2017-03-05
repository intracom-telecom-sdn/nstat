# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Unittest Module for util/plot_json.py."""

import unittest
import util.plot_json

class PlotJsonKeyErrorTests(unittest.TestCase):
    """Unit test class that checks the case of KeyError for all functions in
    module util/plot_json.py.
    """

    def test_errorbar(self):
        """Checks the errorbar() method of util/plot_json.py.
        It checks the case of invalid json input.
        """
        with self.assertRaises(KeyError):
            util.\
            plot_json.plot_json(('./sample_test_json/sample_'
                                 'result_file_with_error.json'), 'switches',
                                'throughput', None,
                                'Number of switches', 'Throughput (flows/sec)',
                                'errorbar', 'Controller throughput',
                                ['java_opts', 'controller'], 'errorbar.png',
                                None, None, 0, None)

    def test_errorbar_connected(self):
        """Checks the errorbar_connected() method of
        util/plot_json.py. It checks the case of invalid json input.
        """
        with self.assertRaises(KeyError):
            util.\
            plot_json.plot_json(('./sample_test_json/sample_result_file_'
                                 'with_error.json'), 'switches',
                                'throughput', None,
                                'Number of switches', 'Throughput (flows/sec)',
                                'errorbar_connected', 'Controller throughput',
                                ['java_opts', 'controller'], 'errorbar.png',
                                None, None,
                                0, None)

    def test_scatter(self):
        """
        Checks the scatter() method of util/plot_json.py.
        It checks the case of invalid json input.
        """
        with self.assertRaises(KeyError):
            util.\
            plot_json.plot_json(('./sample_test_json/sample_result_file'
                                 '_with_error.json'), 'switches',
                                'throughput', None,
                                'Number of switches', 'Throughput (flows/sec)',
                                'scatter', 'Controller throughput',
                                ['java_opts', 'controller'], 'errorbar.png',
                                None, None, 0, None)

    def test_multi_scatter(self):
        """
        Checks the multy_scatter() method of util/plot_json.py
        It checks the case of invalid json input.
        """
        with self.assertRaises(KeyError):
            util.\
            plot_json.plot_json(('./sample_test_json/sample_result_file_with_'
                                 'error.json'), 'switches',
                                'throughput', None,
                                'Number of switches', 'Throughput (flows/sec)',
                                'multi_scatter', 'Controller throughput',
                                ['java_opts', 'controller'], 'errorbar.png',
                                None, None, 0, None)

    def test_multi_errorbar(self):
        """
        Checks the multi_errorbar() function of util/plot_json.py.
        It checks the case of invalid json input.
        """
        with self.assertRaises(KeyError):
            util.\
            plot_json.plot_json(('./sample_test_json/sample_result_file_'
                                 'with_error.json'), 'switches',
                                'throughput', None,
                                'Number of switches', 'Throughput (flows/sec)',
                                'multi_errorbar', 'Controller throughput',
                                ['java_opts', 'controller'], 'errorbar.png',
                                None, None, 0, None)

    def test_multi_errorbar_connected(self):
        """
        Method that checks the multi_errorbar_connected() function of
        util/plot_json.py. It checks the case of invalid json input.
        """
        with self.assertRaises(KeyError):
            util.\
            plot_json.plot_json(('./sample_test_json/sample_result_file'
                                 '_with_error.json'), 'switches',
                                'throughput', None,
                                'Number of switches', 'Throughput (flows/sec)',
                                'multi_errorbar_connected',
                                'Controller throughput',
                                ['java_opts', 'controller'], 'errorbar.png',
                                None, None, 0, None)

if __name__ == '__main__':
    SUITE_PLOTJSONKEYERRORTESTS = unittest.TestLoader().\
    loadTestsFromTestCase(PlotJsonKeyErrorTests)
    unittest.TextTestRunner(verbosity=2).run(SUITE_PLOTJSONKEYERRORTESTS)
