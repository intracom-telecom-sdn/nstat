# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Unittest Module for util/sysstats.py."""

import logging
import os
import subprocess
import sys
import threading
import time
import util.sysstats
import unittest

from random import randint

LOGGER = logging.getLogger()
LOGGER.level = logging.DEBUG
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(STREAM_HANDLER)

def worker_thread():
    """
    Creates a thread used for testing senarios.
    """
    time.sleep(6)
    sys.exit(0)


class MemoryUtilsTest(unittest.TestCase):
    """Unittests for memory functions of the module sysstats.
    """

    def test01_used_ram(self):
        """Test functionality of sysstats.sys_free_ram_mb function.
        """

        var = util.sysstats.sys_used_ram_mb()
        self.assertTrue((var > 0) and isinstance(var, int))

    def test02_free_ram(self):
        """Test functionality of sysstats.sys_free_ram_mb function
        """

        var = util.sysstats.sys_free_ram_mb()
        self.assertTrue((var > 0) and isinstance(var, int))

    def test03_used_ramb(self):
        """Test functionality of sysstats.sys_used_memory_bytes function
        """

        var = util.sysstats.sys_used_memory_bytes()
        self.assertTrue((var > 0) and isinstance(var, int))

    def test04_free_ramb(self):
        """Test functionality of sysstats.sys_free_memory_bytes function
        """

        var = util.sysstats.sys_free_memory_bytes()
        self.assertTrue((var > 0) and isinstance(var, int))

    def test05_totam_ramb(self):
        """Test functionality of sysstats.sys_total_memory_bytes function
        """

        var = util.sysstats.sys_total_memory_bytes()
        self.assertTrue((var > 0) and isinstance(var, int))

class ProcIOTEst(unittest.TestCase):
    """Class that has unittests for process I/O related functions in
    util/sysstats.py"""

    def test01_io_error(self):
        """Test functionality of sysstats.sys_iowait_time function
        """

        var = util.sysstats.sys_iowait_time()
        self.assertTrue((var > 0) and isinstance(var, float))

class ProcVariousPidRelatedTests(unittest.TestCase):
    """Class that has unittests for process ID related functions in
    util/sysstats.py"""

    @classmethod
    def setUpClass(cls):
        """Creates the initial environment to run testcases of this class.
        """

        cls.useless_file_htop = open('useless_file_htop', 'w+')
        cls.useless_file_htop1 = open('useless_file_htop1', 'w+')
        cls.top_process = subprocess.Popen(
            ['htop'],
            stdout=cls.useless_file_htop,
            stderr=cls.useless_file_htop)
        cls.top_pid = cls.top_process.pid
        cls.htop_process = subprocess.Popen(
            ['htop'],
            stdout=cls.useless_file_htop1,
            stderr=cls.useless_file_htop1)
        cls.htop_pid = cls.htop_process.pid
        cls.cur_dir = os.getcwd()
        cls.total_cpus = int(os.popen('nproc').read())
        cls.cmd1 = util.sysstats.proc_cmdline(cls.top_pid)
        cls.cmd2 = util.sysstats.proc_cmdline(cls.htop_pid)

    def test01_cmd_line(self):
        """Test functionality of sysstats.proc_cmdline function
        """

        self.assertEqual(self.cmd1, 'htop')
        self.assertEqual(self.cmd2, 'htop')

    def test02_cwd(self):
        """Test functionality of sysstats.proc_cwd function
        """

        self.assertEqual(self.cur_dir, util.sysstats.proc_cwd(self.top_pid))
        self.assertEqual(self.cur_dir, util.sysstats.proc_cwd(self.htop_pid))

    def test04_cpu_system_time(self):
        """Test functionality of sysstats.proc_cpu_system_time function
        """

        self.assertTrue(
            isinstance(
                util.sysstats.proc_cpu_system_time(
                    self.htop_pid),
                float))
        self.assertTrue(
            isinstance(
                util.sysstats.proc_cpu_system_time(
                    self.top_pid),
                float))

    def test05_vm_size(self):
        """Test functionality of sysstats.proc_vm_size function
        """

        self.assertTrue(isinstance(util.sysstats.proc_vm_size(self.top_pid),
                                   int))
        self.assertTrue(isinstance(util.sysstats.proc_vm_size(self.htop_pid),
                                   int))

    @classmethod
    def tearDownClass(cls):
        """Cleans up the environment after testing.
        """

        cls.top_process.terminate()
        cls.htop_process.terminate()
        os.chdir('./')
        rmrfcommand = 'rm -f useless_file_htop*'
        subprocess.check_output(rmrfcommand, shell=True)
        os.chdir(os.pardir)


class ProcessThreadAndFDsTests(unittest.TestCase):
    """Class used for testing thread functionality and open files"""

    @classmethod
    def setUpClass(cls):
        """Creates the initial environment to run testcases of this class.
        """

        cls.threads = []
        cls.files = []
        cls.num_threads = randint(1, 20)
        cls.num_files = randint(1, 20)
        cls.pid = os.getpid()
        STREAM_HANDLER.stream = sys.stdout
        logging.getLogger().info('Process with pid = %d will '
                                 'create %d threads '
                                 'and %d files.',
                                 cls.pid,
                                 cls.num_threads,
                                 cls.num_files)
        for i in range(0, cls.num_threads):
            w_thread = threading.Thread(target=worker_thread)
            cls.threads.append(w_thread)
            w_thread.start()
            logging.getLogger().info('Starting worker_thread: %d', i)
        for num_file in range(0, cls.num_files):
            open_file = open('./temp_test_file_{0}'.format(num_file), 'w+')
            cls.files.append(open_file)

    def test01_num_fds(self):
        """Test functionality of sysstats.proc_num_fds function
        """

        num_fds = util.sysstats.proc_num_fds(self.pid)
        self.assertTrue(isinstance(num_fds, int))

    def test02_num_threads(self):
        """Test functionality of sysstats.proc_num_threads function
        """

        self.assertEqual(util.sysstats.proc_num_threads(self.pid),
                         self.num_threads + 1)

    @classmethod
    def tearDownClass(cls):
        """Cleans up the environment after testing.
        """

        for thread in cls.threads:
            thread.join()
        os.chdir('./')
        rmrfcommand = 'rm -f temp_test_file*'
        subprocess.check_output(rmrfcommand, shell=True)
        os.chdir(os.pardir)


class SysLoadAverageTest(unittest.TestCase):
    """Unittests for CPU load related functions in util/sysstats.py"""

    def test01_sys_load_average(self):
        """Test functionality of sysstats.sys_load_average function
        """

        self.assertTrue(all(isinstance(sysload, float)
                            for sysload in util.sysstats.sys_load_average()))

if __name__ == '__main__':

    SUITE_MEMORYUTILSTEST = unittest.TestLoader().\
    loadTestsFromTestCase(MemoryUtilsTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE_MEMORYUTILSTEST)

    SUITE_PROCIOTEST = unittest.TestLoader().\
    loadTestsFromTestCase(ProcIOTEst)
    unittest.TextTestRunner(verbosity=2).run(SUITE_PROCIOTEST)

    SUITE_PROCESSTHREADANDFDSTESTS = unittest.TestLoader().\
    loadTestsFromTestCase(ProcVariousPidRelatedTests)
    unittest.TextTestRunner(verbosity=2).run(SUITE_PROCESSTHREADANDFDSTESTS)

    SUITE_PROCESSTHREADANDFDSTESTS = unittest.TestLoader().\
    loadTestsFromTestCase(ProcessThreadAndFDsTests)
    unittest.TextTestRunner(verbosity=2).run(SUITE_PROCESSTHREADANDFDSTESTS)

    SUITE_SYSLOADAVERAGETEST = unittest.TestLoader().\
    loadTestsFromTestCase(SysLoadAverageTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE_SYSLOADAVERAGETEST)
