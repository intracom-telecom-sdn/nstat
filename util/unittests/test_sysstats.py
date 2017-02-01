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
import unittest
import util.netutil
import util.sysstats


from random import randint

LOGGER = logging.getLogger()
LOGGER.level = logging.DEBUG
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(STREAM_HANDLER)
SSH_IP = '127.0.0.1'
SSH_UNAME = 'jenkins'
SSH_PWD = 'jenkins'


def worker_thread():
    """
    Creates a thread used for testing senarios.
    """
    time.sleep(6)
    sys.exit(0)


class MemoryUtilsTest(unittest.TestCase):
    """Unittests for memory functions of the module sysstats.
    """

    @classmethod
    def setUpClass(cls):
        """Creates the initial environment to run testcases of this class.
        """
        cls.ssh_client = util.netutil.ssh_connect_or_return(SSH_IP, 22,
                                                            SSH_UNAME, SSH_PWD,
                                                            10)

    def test01_used_ram(self):
        """Test functionality of sysstats.sys_free_ram_mb function.
        """

        var = util.sysstats.sys_used_ram_mb()
        self.assertTrue((var > 0) and isinstance(var, int),
                        'Testing without using ssh_client')
        var = util.sysstats.sys_used_ram_mb(self.ssh_client)
        self.assertTrue((var > 0) and isinstance(var, int),
                        'Testing using ssh_client')

    def test02_free_ram(self):
        """Test functionality of sysstats.sys_free_ram_mb function
        """

        var = util.sysstats.sys_free_ram_mb()
        self.assertTrue((var > 0) and isinstance(var, int),
                        'Testing without using ssh_client')
        var = util.sysstats.sys_free_ram_mb(self.ssh_client)
        self.assertTrue((var > 0) and isinstance(var, int),
                        'Testing using ssh_client')

    def test03_used_ramb(self):
        """Test functionality of sysstats.sys_used_memory_bytes function
        """

        var = util.sysstats.sys_used_memory_bytes()
        self.assertTrue((var > 0) and isinstance(var, int),
                        'Testing without using ssh_client')
        var = util.sysstats.sys_used_memory_bytes(self.ssh_client)
        self.assertTrue((var > 0) and isinstance(var, int),
                        'Testing using ssh_client')

    def test04_free_ramb(self):
        """Test functionality of sysstats.sys_free_memory_bytes function
        """

        var = util.sysstats.sys_free_memory_bytes()
        self.assertTrue((var > 0) and isinstance(var, int),
                        'Testing without using ssh_client')
        var = util.sysstats.sys_free_memory_bytes(self.ssh_client)
        self.assertTrue((var > 0) and isinstance(var, int),
                        'Testing using ssh_client')

    def test05_totam_ramb(self):
        """Test functionality of sysstats.sys_total_memory_bytes function
        """

        var = util.sysstats.sys_total_memory_bytes()
        self.assertTrue((var > 0) and isinstance(var, int),
                        'Testing without using ssh_client')
        var = util.sysstats.sys_total_memory_bytes(self.ssh_client)
        self.assertTrue((var > 0) and isinstance(var, int),
                        'Testing using ssh_client')

    @classmethod
    def tearDownClass(cls):
        """Cleans up the environment after testing.
        """
        cls.ssh_client.close()


class ProcIOTEst(unittest.TestCase):
    """Class that has unittests for process I/O related functions in
    util/sysstats.py"""

    @classmethod
    def setUpClass(cls):
        """Creates the initial environment to run testcases of this class.
        """
        cls.ssh_client = util.netutil.ssh_connect_or_return(SSH_IP, 22,
                                                            SSH_UNAME, SSH_PWD,
                                                            10)

    def test01_io_error(self):
        """Test functionality of sysstats.sys_iowait_time function
        """
        var = util.sysstats.sys_iowait_time()
        self.assertTrue((var > 0) and isinstance(var, float),
                        'Testing without using ssh_client')
        var = util.sysstats.sys_iowait_time(self.ssh_client)
        self.assertTrue((var > 0) and isinstance(var, float),
                        'Testing using ssh_client')

    @classmethod
    def tearDownClass(cls):
        """Cleans up the environment after testing.
        """
        cls.ssh_client.close()

class ProcVariousPidRelatedTests(unittest.TestCase):
    """Class that has unittests for process ID related functions in
    util/sysstats.py"""

    @classmethod
    def setUpClass(cls):
        """Creates the initial environment to run testcases of this class.
        """
        cls.ssh_client = util.netutil.ssh_connect_or_return(SSH_IP, 22,
                                                            SSH_UNAME, SSH_PWD,
                                                            10)
        cls.useless_file_htop_local = open('useless_file_htop_local', 'w+')
        cls.htop_process_local = subprocess.Popen(
            ['htop'],
            stdout=cls.useless_file_htop_local,
            stderr=cls.useless_file_htop_local)
        cls.htop_pid_local = cls.htop_process_local.pid
        cls.cur_dir_local = os.getcwd()
        cls.total_cpus_local = int(os.popen('nproc').read())
        cls.cmd_local = util.sysstats.proc_cmdline(cls.htop_pid_local)
        util.netutil.ssh_run_command(
            cls.ssh_client, 'sleep 1000 & echo $! > sleep_pid.txt', prefix='',
            lines_queue=None, print_flag=True, block_flag=False)
        cls.exit_status, cls.sleep_pid_remote = \
            util.netutil.ssh_run_command(cls.ssh_client, 'cat sleep_pid.txt')
        cls.sleep_pid_remote = cls.sleep_pid_remote.strip()
        cls.exit_status, cls.cur_dir_remote = \
            util.netutil.ssh_run_command(cls.ssh_client, 'pwd')
        cls.cur_dir_remote = cls.cur_dir_remote.strip()
        cls.exit_status, cls.total_cpus_remote = \
            util.netutil.ssh_run_command(cls.ssh_client,
                'cat /proc/cpuinfo | grep processor | wc -l')
        cls.cmd_remote = util.sysstats.proc_cmdline(cls.sleep_pid_remote,
                                                    cls.ssh_client)

    def test01_cmd_line(self):
        """Test functionality of sysstats.proc_cmdline function
        """
        self.assertEqual(self.cmd_local, 'htop',
                         'Testing without using ssh_client')
        self.assertEqual(self.cmd_remote, 'sleep1000',
                         'Testing using ssh_client')

    def test02_cwd(self):
        """Test functionality of sysstats.proc_cwd function
        """

        self.assertEqual(self.cur_dir_local, util.sysstats.proc_cwd(
            self.htop_pid_local), 'Testing without using ssh_client')
        self.assertEqual(self.cur_dir_remote.strip(), util.sysstats.proc_cwd(
            self.sleep_pid_remote, self.ssh_client),
            'Testing using ssh_client')

    def test04_cpu_system_time(self):
        """Test functionality of sysstats.proc_cpu_system_time function
        """

        self.assertTrue(
            isinstance(
                util.sysstats.proc_cpu_system_time(self.htop_pid_local),
                float), 'Testing without using ssh_client')
        self.assertTrue(
            isinstance(
                util.sysstats.proc_cpu_system_time(self.sleep_pid_remote,
                                                   self.ssh_client),
                float), 'Testing using ssh_client')

    def test05_vm_size(self):
        """Test functionality of sysstats.proc_vm_size function
        """

        self.assertTrue(isinstance(util.sysstats.proc_vm_size(
            self.htop_pid_local), int), 'Testing without using ssh_client')
        self.assertTrue(isinstance(util.sysstats.proc_vm_size(
            self.htop_pid_local, self.ssh_client), int),
            'Testing using ssh_client')

    @classmethod
    def tearDownClass(cls):
        """Cleans up the environment after testing.
        """

        cls.htop_process_local.terminate()
        os.chdir('./')
        rmrfcommand = 'rm -f useless_file_htop*'
        subprocess.check_output(rmrfcommand, shell=True)
        os.chdir(os.pardir)
        util.netutil.ssh_run_command(cls.ssh_client, 'pkill sleep',
                                     prefix='[Unittesting]', lines_queue=None,
                                     print_flag=True, block_flag=False)
        cls.ssh_client.close()


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
        cls.ssh_client = util.netutil.ssh_connect_or_return(SSH_IP,
            SSH_UNAME, SSH_PWD, 10, 22)
        util.netutil.ssh_run_command(cls.ssh_client,
            'sleep 1000 & echo $! > sleep_pid.txt', prefix='',
            lines_queue=None, print_flag=True, block_flag=False)
        cls.exit_status, cls.sleep_pid_remote = \
            util.netutil.ssh_run_command(cls.ssh_client, 'cat sleep_pid.txt')
        cls.sleep_pid_remote = cls.sleep_pid_remote.strip()
        cls.exit_status, cls.num_remote_threads = \
            util.netutil.ssh_run_command(cls.ssh_client,
                'cat /proc/{0}/status |grep Threads | awk \'{{print $2}}\''.
                format(cls.sleep_pid_remote))
        cls.num_remote_threads = int(cls.num_remote_threads.strip())
        cls.exit_status, cls.num_remote_fds = \
            util.netutil.ssh_run_command(cls.ssh_client,
                'ls -l /proc/{0}/fd | wc -l'.format(cls.sleep_pid_remote))
        cls.num_remote_fds = int(cls.num_remote_fds.strip()) -3

    def test01_num_fds(self):
        """Test functionality of sysstats.proc_num_fds function
        """

        num_fds_local = util.sysstats.proc_num_fds(self.pid)
        self.assertTrue(isinstance(num_fds_local, int),
                        'Testing without using ssh_client')
        num_fds_remote = util.sysstats.proc_num_fds(self.sleep_pid_remote)
        self.assertTrue(isinstance(num_fds_remote, int),
                        'Testing using ssh_client')

    def test02_num_threads(self):
        """Test functionality of sysstats.proc_num_threads function
        """

        self.assertEqual(util.sysstats.proc_num_threads(self.pid),
                         self.num_threads+2,
                         'Testing without using ssh_client')

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
        util.netutil.ssh_run_command(cls.ssh_client, 'pkill sleep',
            prefix='[Unittesting]', lines_queue=None, print_flag=True,
            block_flag=False)
        cls.ssh_client.close()


class SysLoadAverageTest(unittest.TestCase):
    """Unittests for CPU load related functions in util/sysstats.py"""

    @classmethod
    def setUpClass(cls):
        """Creates the initial environment to run testcases of this class.
        """
        cls.ssh_client = util.netutil.ssh_connect_or_return(SSH_IP,
            SSH_UNAME, SSH_PWD, 10, 22)

    def test01_sys_load_average(self):
        """Test functionality of sysstats.sys_load_average function
        """

        self.assertTrue(all(isinstance(sysload, float)
                            for sysload in util.sysstats.sys_load_average()),
                         'Testing without using ssh_client')
        self.assertTrue(all(isinstance(sysload, float)
            for sysload in util.sysstats.sys_load_average(self.ssh_client)),
            'Testing using ssh_client')

    @classmethod
    def tearDownClass(cls):
        """Cleans up the environment after testing.
        """
        cls.ssh_client.close()

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
