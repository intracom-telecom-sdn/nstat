# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" file handling utilities """

import os
import stat


def check_files_exist(file_list):
    """Checks if all files in a list exist.

    :param file_list: list of filenames to check
    :type file_list: list<str>
    :returns: list<str>
    :rtype: list<str>
    """

    return [f for f in file_list if not file_exists(f)]

def check_files_executables(file_list):
    """Checks if all files in a list have exe permissions.

    :param file_list: list of filenames to check
    :raises Exception: When file in file_list does not exist or is not
    executable.
    :type file_list: list<str>
    :returns: list<str>
    :rtype: list<str>
    """

    return [f for f in file_list if not is_file_exe(f)]

def check_filelist(file_list):
    """Takes a list of files and checks if those files exist and if those
    files are executables (have execution right in their privileges). If
    something is wrong then an exception is raised

    :param file_list: A list of files
    :type file_list: list<str>
    """

    filelst = check_files_exist(file_list)
    if filelst != []:
        raise Exception('Files {0} do not exist.'.format(filelst))
    filelst = check_files_executables(file_list)
    if filelst != []:
        raise Exception('Files {0} are not executable.'.format(filelst))

def file_exists(fpath):
    """Checks if file exists in filesystem.

    :param fpath: file path to check
    :type fpath: str
    :returns: bool
    :rtype: bool
    """

    return os.path.isfile(fpath)

def is_file_exe(fpath):
    """Checks if a file is executable.

    :param fpath: file path to check
    :type fpath: str
    :returns: bool
    :rtype: bool
    """

    return os.access(fpath, os.X_OK)

def make_file_exe(fpath):
    """Gives executable rights to a file.

    :param fpath: file path to handle
    :type fpath: str
    """

    statinfo = os.stat(fpath)
    os.chmod(fpath, statinfo.st_mode | stat.S_IEXEC)