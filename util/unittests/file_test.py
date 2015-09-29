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

class DefineTestFolder():
    """Defines within __init__ self.virtualfolder to become available
    within all methods of FileTestFileExist()
    Methods tested: testing file.py: --
    """

    def __init__(self):
        self.virtualfolder = "testfolder"


class FileTestFileExist(unittest.TestCase):
    """Contains methods for testing methods within file.py
    Methods checked: testing file.py: file_exists, is_file_exe, make_file_exe
    check_files_exist, check_files_executable
    """

    def setUp(self):
        """Creates a batch of files stored under fillist (filelist =
        namlist x extlist). Created files are stored under self.virtualfolder
        which is removed in tearDown()
        """
        self.dfnstfldr = DefineTestFolder()
        virtualfolder = self.dfnstfldr.virtualfolder

        # Check virtualfolder existence if exists remove
        if os.path.exists(virtualfolder):
            shutil.rmtree(virtualfolder)

        namlist = ['foo1', 'foo2', 'foo3',
                   'foo4', 'foo5', 'foo6',
                   'foo7', 'foo8', 'foo9']
        extlist = ['.txt', '.mp3', '.mp4',
                   '.avi', '.sh', '.png', '.jpg']
        fillist = []

        for res in itertools.product(namlist, extlist):
            joinedname = ''.join(res)
            fillist.append(joinedname)

        fillistlength = len(fillist)
        subprocess.check_output(["mkdir", virtualfolder])
        for i in range(0, fillistlength):
            subprocess.check_output(["touch", fillist[i]])
            mvcommand = 'mv' + ' ' + fillist[i] + ' ' + virtualfolder
            subprocess.check_output(mvcommand, shell=True)

    def tearDown(self):
        """Deletes the batch of files stored created at setUp() and
        stored under self.virtualfolder
        """

        self.dfnstfldr = DefineTestFolder()
        virtualfolder = self.dfnstfldr.virtualfolder
        removetestfoldercommand = 'rm -rf' + ' ' + virtualfolder
        subprocess.check_output(removetestfoldercommand, shell=True)

    def test01_file_exists(self):
        """Checks if foo1.txt exists within self.virtualfolder folder
        """

        self.dfnstfldr = DefineTestFolder()
        virtualfolder = self.dfnstfldr.virtualfolder
        filepath = './' + virtualfolder + '/' + 'foo1.txt'
        self.assertTrue(f.file_exists(filepath))

    def test02_file_exists(self):
        """Checks if foo2.txt exists within the self.virtualfolder
        folder
        """

        self.dfnstfldr = DefineTestFolder()
        virtualfolder = self.dfnstfldr.virtualfolder
        filepath = './' + virtualfolder + '/' + 'foo2.txt'
        self.assertTrue(f.file_exists(filepath))

    def test03_file_exists(self):
        """Checks if foo3.txt exist within the self.virtualfolder.
        """

        self.dfnstfldr = DefineTestFolder()
        virtualfolder = self.dfnstfldr.virtualfolder
        filepath = './' + virtualfolder + '/' + 'foo3.txt'
        self.assertTrue(f.file_exists(filepath))

    def test04_is_file_exe(self):
        """Checks if foo1.txt within the self.virtualfolder is exe.
        """

        self.dfnstfldr = DefineTestFolder()
        virtualfolder = self.dfnstfldr.virtualfolder
        filepath = './' + virtualfolder + '/' + 'foo1.txt'
        chmode = 0o777
        os.chmod(filepath, chmode)
        self.assertTrue(f.is_file_exe(filepath))

    def test05_is_file_exe(self):
        """Checks if foo2.txt within the self.virtualfolder is exe.
        """

        self.dfnstfldr = DefineTestFolder()
        virtualfolder = self.dfnstfldr.virtualfolder
        filepath = './' + virtualfolder + '/' + 'foo2.sh'
        chmode = 0o770
        os.chmod(filepath, chmode)
        self.assertTrue(f.is_file_exe(filepath))

    def test06_make_file_exe(self):
        """
        Method that checks if foo2.sh file within the self.virtualfolder is exe.
        """
        self.dfnstfldr = DefineTestFolder()
        virtualfolder = self.dfnstfldr.virtualfolder
        filepath = './' + virtualfolder + '/' + 'foo2.sh'
        f.make_file_exe(filepath)
        self.assertTrue(f.is_file_exe(filepath))


    def test07_check_files_exist(self):
        """Checks if files within tstlist are all existing with the
        self.virtualfolder
        """

        # Define the test folder list.
        tstlist = ['foo1.txt', 'foo1.mp3', 'foo1.avi',
                   'foo2.txt', 'foo2.txt', 'foo2.txt', ]

        self.dfnstfldr = DefineTestFolder()
        virtualfolder = self.dfnstfldr.virtualfolder

        # Change to the virtualfolder directory and test the tstlist if files
        # exist with the virtualfolder
        os.chdir(virtualfolder)
        reslist = f.check_files_exist(tstlist)
        self.assertListEqual(reslist, [], 'some files do not exist')

        # Return to parent directory after test is over and continue
        os.chdir(os.pardir)

    def test08_check_files_executables(self):
        """Modifies recursively self.virtualfolder so that all
        files become executables and tests if all files within the
        self.virtualfolder are executables
        """

        # Change to the virtualfolder directory and 'chmod 777' to all files
        # within the virtualfolder
        self.dfnstfldr = DefineTestFolder()
        virtualfolder = self.dfnstfldr.virtualfolder

        # 'chmod' of all files within virtualfolder with 777
        chmode = '777'
        chmodcommand = 'chmod' + ' ' + '-R' + ' ' + chmode + ' ' + virtualfolder
        subprocess.check_output(chmodcommand, shell=True)

        # Get list of files from virtualfolder
        tstlist = os.listdir(virtualfolder)

        os.chdir(virtualfolder)
        reslist = f.check_files_executables(tstlist)
        self.assertListEqual(reslist, [], 'list is NOT empty')

        # Return to parent directory after test is over and continue
        os.chdir(os.pardir)

if __name__ == '__main__':
    SUITE_FILE_TEST = unittest.TestLoader().\
                             loadTestsFromTestCase(FileTestFileExist)
    unittest.TextTestRunner(verbosity=2).run(SUITE_FILE_TEST)
