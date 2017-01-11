# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Implementation of custom NB generator exception classes."""


class NBGenError(Exception):

    def __init__(self, err_msg=None, err_code=1):
        """Base-class for all NB generator exceptions raised by this module.
        :param err_msg: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        self.err_code = err_code
        if err_msg is None:
            Exception.__init__(self, 'NB generator generic exception')
            self.err_msg = 'NB generator generic exception'
        else:
            Exception.__init__(self, err_msg)
            self.err_msg = err_msg


class NBGenNodeConnectionError(NBGenError):

    def __init__(self, additional_error_info='', err_code=1):
        """A NB generator node connection error."""
        NBGenError.__init__(self, 'Fail to establish ssh connection with '
                            'NB generator node. {0}'.
                            format(additional_error_info), err_code)


class NBGenBuildError(NBGenError):

    def __init__(self, additional_error_info='', err_code=1):
        """NB generator build failure.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        NBGenError.__init__(self, 'Fail to build NB generator. {0}'.
                            format(additional_error_info), err_code)


class NBGenCleanError(NBGenError):

    def __init__(self, additional_error_info='', err_code=1):
        """NB generator clean failure.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        NBGenError.__init__(self, 'Fail to cleaning NB generator. {0}'.
                            format(additional_error_info), err_code)


class NBGenRunError(NBGenError):

    def __init__(self, additional_error_info='', err_code=1):
        """NB generator run failure.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        NBGenError.__init__(self, 'Fail to run NB generator. {0}'.
                            format(additional_error_info), err_code)


class NBGenGetOperFlowsError(NBGenError):

    def __init__(self, additional_error_info='', err_code=1):
        """NB generator handler of getting operational flows failure.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        NBGenError.__init__(self, 'Failure during getting operational '
                            'flows. {0}'.format(additional_error_info),
                            err_code)


class NBGenPollDSError(NBGenError):

    def __init__(self, additional_error_info='', err_code=1):
        """NB generator failure during datastore polling.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        NBGenError.__init__(self, 'Fail during datastore polling. {0}'.
                            format(additional_error_info), err_code)


class NBGenPollOVSError(NBGenError):

    def __init__(self, additional_error_info='', err_code=1):
        """NB generator failure during OpenVSwitch polling.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        NBGenError.__init__(self, 'Fail during OpenVSwitch. {0}'.
                            format(additional_error_info), err_code)


class NBGenMonitorRunError(NBGenError):

    def __init__(self, additional_error_info='', err_code=1):
        """Error during running monitor threads.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        NBGenError.__init__(self, 'Failure in monitor run. {0}'.
                            format(additional_error_info), err_code)
