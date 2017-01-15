# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Implementation of custom oftraf exception classes."""


class OftrafError(Exception):
    """Contains the exception handling concerning the Oftraf class
    functionalities.
    """
    def __init__(self, err_msg=None, err_code=1):
        """Base-class for all oftraf exceptions raised by this module.
        :param err_msg: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        self.err_code = err_code
        if err_msg is None:
            Exception.__init__(self, 'Oftraf generic exception')
            self.err_msg = 'Oftraf generic exception'
        else:
            Exception.__init__(self, err_msg)
            self.err_msg = err_msg


class OftrafBuildError(OftrafError):
    """Contains the exception handling concerning the Oftraf building
    functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """An oftraf build error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        OftrafError.__init__(self, 'Fail to build oftraf (git clone). {0}'.
                             format(additional_error_info), err_code)


class OftrafStartError(OftrafError):
    """Contains the exception handling concerning the Oftraf starting
    functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """An oftraf start error."""
        OftrafError.__init__(self, 'Fail to start oftraf. {0}'.
                             format(additional_error_info), err_code)


class OftrafStopError(OftrafError):
    """Contains the exception handling concerning the Oftraf stopping
    functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """An oftraf stop error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        OftrafError.__init__(self, 'Fail to stop oftraf. {0}'.
                             format(additional_error_info), err_code)


class OftrafCleanError(OftrafError):
    """Contains the exception handling concerning the Oftraf measurements
    (packet counts) functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """An oftraf clean error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        OftrafError.__init__(self, 'Fail to clean oftraf. {0}'.
                             format(additional_error_info), err_code)


class OftrafGetResultError(OftrafError):
    """Contains the exception handling concerning the Oftraf cleaning
    functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """An oftraf get results error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        OftrafError.__init__(self, 'Fail to get results. {0}'.
                             format(additional_error_info), err_code)
