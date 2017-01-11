# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Implementation of custom controller exception classes."""


class CtrlError(Exception):

    def __init__(self, err_msg=None, err_code=1):
        """Base-class for all controller exceptions raised by this module.
        :param err_msg: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        self.err_code = err_code
        if err_msg is None:
            Exception.__init__(self, 'Controller generic exception')
            self.err_msg = 'Controller generic exception'
        else:
            Exception.__init__(self, err_msg)
            self.err_msg = err_msg


class CtrlNodeConnectionError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """A controller node connection error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'Fail to establish ssh connection with '
                                 'controller node. {0}'.
                                 format(additional_error_info), err_code)


class CtrlBuildError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """A controller build error
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'Controller build failure. {0}'.
                                 format(additional_error_info), err_code)


class CtrlStartError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """A controller start error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'Controller start failure. {0}'.
                                 format(additional_error_info), err_code)


class CtrlStopError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """A controller stop error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'Controller stop failure. {0}'.
                                 format(additional_error_info), err_code)


class CtrlCleanupError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """A controller cleanup error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'Controller cleanup failure. {0}'.
                                 format(additional_error_info), err_code)


class CtrlStatusUnknownError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """A controller status unknown error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'Controller fail to get status. {0}'.
                                 format(additional_error_info), err_code)


class CtrlReadyStateError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """A controller ready state error."""
        CtrlError.__init__(self, 'Controller did not reach '
                                 'ready state. {0}'.
                                 format(additional_error_info), err_code)


class CtrlPortConflictError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """A controller port conflict error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'Controller SouthBound port is in '
                                 'use by another process. {0}'.
                                 format(additional_error_info), err_code)


class ODLXMLError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """ODL XML generation error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'ODL Fail to generate XML files. {0}'.
                                 format(additional_error_info), err_code)


class ODLDisablePersistenceError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """ODL fail to disable persistence error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'ODL Fail to disable persistence mode. {0}'.
                                 format(additional_error_info), err_code)


class ODLChangeStats(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """ODL fail to change statistics period error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'ODL Fail to change statistics period. {0}'.
                                 format(additional_error_info), err_code)


class ODLFlowModConfError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """ODL fail to configure for flow modifications send error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'ODL Fail to make configuration to send '
                           'flow modifications. {0}'.
                           format(additional_error_info), err_code)


class ODLGetOperHostsError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """ODL fail to get hosts from operational datastore error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'ODL fail to get hosts from '
                           'operational datastore. {0}'.
                           format(additional_error_info), err_code)


class ODLGetOperFlowsError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """ODL fail to get installed flows from operational datastore error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'ODL fail to get installed flows from '
                           'operational datastore. {0}'.
                           format(additional_error_info), err_code)


class ODLGetOperSwitchesError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """ODL fail to get topology switches from operational datastore error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'ODL fail to get topology switches from '
                           'operational datastore. {0}'.
                           format(additional_error_info), err_code)


class ODLGetOperLinksError(CtrlError):

    def __init__(self, additional_error_info='', err_code=1):
        """ODL fail to get topology links from operational datastore error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        CtrlError.__init__(self, 'ODL fail to get topology links from '
                           'operational datastore. {0}'.
                           format(additional_error_info), err_code)
