# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Unittest Module for util/file.py."""

import itertools
import os
import shutil
import subprocess
import unittest
import util.file_ops as f


class FileTestFileExist(unittest.TestCase):
    """Contains methods for testing methods within file.py
    Methods checked: testing file.py: file_exists, is_file_exe, make_file_exe
    check_files_exist, check_files_executable
    """
    def createfile(self):
        pass

    @classmethod
    def setUpClass(cls):
        """Creates a batch of files stored under fillist (filelist =
        namlist x extlist). Created files are stored under self.virtualfolder
        """
        cls.virtualfolder = "testfolder"
        if os.path.exists(cls.virtualfolder):
            shutil.rmtree(cls.virtualfolder)
        subprocess.check_output(["mkdir", cls.virtualfolder])
        fillist = []
        namlist = ['foo1', 'foo2', 'foo3', 'foo4', 'foo5', 'foo6', 'foo7']
        extlist = ['.txt', '.mp3', '.mp4', '.avi', '.sh', '.png', '.jpg']
        cls.tstlist = ['foo1.txt', 'foo1.mp3', 'foo1.avi', 'foo2.txt']
        cls.chmode = [0o777, 0o777, 777]

        for res in itertools.product(namlist, extlist):
            joinedname = ''.join(res)
            fillist.append(joinedname)

        for i in range(0, len(fillist)):
            subprocess.check_output(["touch", fillist[i]])
            mvcommand = 'mv' + ' ' + fillist[i] + ' ' + cls.virtualfolder
            subprocess.check_output(mvcommand, shell=True)
        index = 3
        cls.filepath = []
        while index != 0:
            name = './' + cls.virtualfolder + '/' + 'foo' + str(index) + '.txt'
            cls.filepath.append(name)
            index -= 1

    def test_file_exists_01(self):
        """Checks if foo1.txt exists within self.virtualfolder folder
        """
        self.assertTrue(f.file_exists(self.filepath[0]))

    def test_file_exists_02(self):
        """Checks if foo2.txt exists within the self.virtualfolder folder
        """
        self.assertTrue(f.file_exists(self.filepath[1]))

    def test_file_exists_03(self):
        """Checks if foo3.txt exist within the self.virtualfolder.
        """
        self.assertTrue(f.file_exists(self.filepath[2]))

    def test_is_file_exe(self):
        """Checks if foo1.txt within the self.virtualfolder is exe
        """
        os.chmod(self.filepath[0], self.chmode[0])
        self.assertTrue(f.is_file_exe(self.filepath[0]))

    def test_check_files_exist(self):
        """Checks file existence within the virtualfolder
        """
        # Change to the virtualfolder directory and test the tstlist if files
        # exist with the virtualfolder
        os.chdir(self.virtualfolder)
        reslist = f.check_files_exist(self.tstlist)
        self.assertListEqual(reslist, [], 'some files do not exist')

        # Return to parent directory after test is over and continue
        os.chdir(os.pardir)

    def test_check_files_executables(self):
        """Modifies recursively self.virtualfolder so that all
        files become executables and tests if all files within the
        self.virtualfolder are executables
        """
        # 'chmod' of all files within virtualfolder with 777
        chmodcommand = 'chmod' + ' ' + '-R' + ' ' + str(self.chmode[2]) + ' ' \
                     + self.virtualfolder
        subprocess.check_output(chmodcommand, shell=True)

        # Get list of files from virtualfolder
        tstlist = os.listdir(self.virtualfolder)

        os.chdir(self.virtualfolder)
        reslist = f.check_files_executables(tstlist)
        self.assertListEqual(reslist, [], 'list is NOT empty')

        # Return to parent directory after test is over and continue
        os.chdir(os.pardir)

    @classmethod
    def tearDownClass(cls):
        """Deletes the batch of files stored created at setUpClass() and
        stored under virtualfolder
        """
        removetestfoldercommand = 'rm -rf' + ' ' + cls.virtualfolder
        subprocess.check_output(removetestfoldercommand, shell=True)

if __name__ == '__main__':
    SUITE_FILE_TEST = unittest.TestLoader().\
                             loadTestsFromTestCase(FileTestFileExist)
    unittest.TextTestRunner(verbosity=2).run(SUITE_FILE_TEST)
