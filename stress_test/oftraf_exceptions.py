# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Implementation of custom oftraf exception classes."""


class OftrafError(Exception):
    """Base-class for all oftraf exceptions raised by this module."""
    def __init__(self, err_msg=None, err_code=1):
        self.err_code = err_code
        if err_msg is None:
            Exception.__init__(self, 'Oftraf generic exception')
            self.err_msg = 'Oftraf generic exception'
        else:
            Exception.__init__(self, err_msg)
            self.err_msg = err_msg


class OftrafBuildError(OftrafError):
    """An oftraf build error."""
    def __init__(self, additional_error_info='', err_code=1):
        OftrafError.__init__(self, 'Fail to build oftraf (git clone). {0}'.
                             format(additional_error_info), err_code)


class OftrafStartError(OftrafError):
    """An oftraf start error."""
    def __init__(self, additional_error_info='', err_code=1):
        OftrafError.__init__(self, 'Fail to start oftraf. {0}'.
                             format(additional_error_info), err_code)


class OftrafStopError(OftrafError):
    """An oftraf stop error."""
    def __init__(self, additional_error_info='', err_code=1):
        OftrafError.__init__(self, 'Fail to stop oftraf. {0}'.
                             format(additional_error_info), err_code)


class OftrafCleanError(OftrafError):
    """An oftraf clean error."""
    def __init__(self, additional_error_info='', err_code=1):
        OftrafError.__init__(self, 'Fail to clean oftraf. {0}'.
                             format(additional_error_info), err_code)


class OftrafGetResultError(OftrafError):
    """An oftraf get results error."""
    def __init__(self, additional_error_info='', err_code=1):
        OftrafError.__init__(self, 'Fail to get results. {0}'.
                             format(additional_error_info), err_code)
