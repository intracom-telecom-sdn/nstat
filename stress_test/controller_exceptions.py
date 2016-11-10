# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Implementation of custom controller exception classes."""


class CtrlError(Exception):
    """Base-class for all controller exceptions raised by this module."""
    def __init__(self, err_msg=None, err_code=1):
        self.err_code = err_code
        if err_msg is None:
            Exception.__init__(self, "Controller generic exception")
            self.err_msg = "Controller generic exception"
        else:
            Exception.__init__(self, err_msg)
            self.err_msg = err_msg


class CtrlNodeConnectionError(CtrlError):
    """"A controller node connection error."""
    def __init__(self, additional_error_info=""):
        CtrlError.__init__(self, "Fail to establish ssh connection with "
                                 "controller node. {0}".
                                 format(additional_error_info))


class CtrlBuildError(CtrlError):
    """"A controller build error."""
    def __init__(self, additional_error_info=""):
        CtrlError.__init__(self, "Controller build failure. {0}".
                                 format(additional_error_info))


class CtrlStartError(CtrlError):
    """"A controller start error."""
    def __init__(self, additional_error_info=""):
        CtrlError.__init__(self, "Controller start failure. {0}".
                                 format(additional_error_info))


class CtrlStopError(CtrlError):
    """"A controller stop error."""
    def __init__(self, additional_error_info=""):
        CtrlError.__init__(self, "Controller stop failure. {0}".
                                 format(additional_error_info))


class CtrlCleanupError(CtrlError):
    """"A controller cleanup error."""
    def __init__(self, additional_error_info=""):
        CtrlError.__init__(self, "Controller cleanup failure. {0}".
                                 format(additional_error_info))


class CtrlStatusUnknownError(CtrlError):
    """"A controller status unknown error."""
    def __init__(self, additional_error_info=""):
        CtrlError.__init__(self, "Controller fail to get status. {0}".
                                 format(additional_error_info))


class CtrlReadyStateError(CtrlError):
    """"A controller ready state error."""
    def __init__(self, additional_error_info=""):
        CtrlError.__init__(self, "Controller did not reach "
                                 "ready state. {0}".
                                 format(additional_error_info))


class CtrlPortConflictError(CtrlError):
    """"A controller port conflict error."""
    def __init__(self, additional_error_info=""):
        CtrlError.__init__(self, "Controller SouthBound port is in "
                                 "use by another process. {0}".
                                 format(additional_error_info))
