# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" file handling utilities """

import os
import stat

def file_exists(fpath):
    """
    Check if file exists in filesystem.
    :param fpath: file path to check
    :return: boolean
    """
    return os.path.isfile(fpath)

def is_file_exe(fpath):
    """
    Check if file is executable.
    :param fpath: file path to check
    :return: boolean
    """
    return os.access(fpath, os.X_OK)

def make_file_exe(fpath):
    """
    Give executable rights to a file.
    :param fpath: file path to handle
    """
    st = os.stat(fpath)
    os.chmod(fpath, st.st_mode | stat.S_IEXEC)

def check_files_exist(file_list):
    """
    Checks if all files in a list exist.
    :param file_list: list of filenames to check
    :return: empty list if all files exist, non-existing files otherwise
    """
    return [f for f in file_list if not file_exists(f)]

def check_files_executables(file_list):
    """
    Checks if all files in a list have exe permissions.
    :param file_list: list of filenames to check
    :return: empty list if all files exist, non-executable files otherwise
    """
    return [f for f in file_list if not is_file_exe(f)]
