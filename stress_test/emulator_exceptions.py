# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Implementation of custom SB emulator exception classes."""


class SBEmuError(Exception):
    """Contains the exception handling concerning the South-Bound Emulator
    class functionalities.
    """
    def __init__(self, err_msg=None, err_code=1):
        """Base-class for all SB emulators exceptions raised by this module.
        :param err_msg: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        self.err_code = err_code
        if err_msg is None:
            Exception.__init__(self, 'SB emulator generic exception')
            self.err_msg = 'SB emulator generic exception'
        else:
            Exception.__init__(self, err_msg)
            self.err_msg = err_msg


class SBEmuNodeConnectionError(SBEmuError):
    """Contains the exception handling concerning the South-Bound Emulator class
    connectivity.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """A SB emulator node connection error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Fail to establish ssh connection with '
                            'SB emulator node. {0}'.
                            format(additional_error_info), err_code)


class SBEmuBuildError(SBEmuError):
    """Contains the exception handling concerning the South-Bound Emulator
    building functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """A SB emulator build error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'SB emulator build failure. {0}'.
                            format(additional_error_info), err_code)


class SBEmuCleanupError(SBEmuError):
    """Contains the exception handling concerning the South-Bound Emulator
    cleaning functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """A SB emulator cleanup error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'SB emulator cleanup failure. {0}'.
                            format(additional_error_info), err_code)


class MTCbenchRunError(SBEmuError):
    """Contains the exception handling concerning the South-Bound Emulator
    running functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """MTCbench fail to run error.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Error occurred while running MTCbench. {0}'.
                            format(additional_error_info), err_code)


class MultinetConfGenerateError(SBEmuError):
    """Contains the exception handling concerning the South-Bound Emulator
    building functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """Fail generate configuration file for multinet
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Error occurred while generating multinet '
                            'configuration file. {0}'.
                            format(additional_error_info), err_code)


class MultinetOutputParsingError(SBEmuError):
    """Contains the exception handling concerning the console output from
    the South-Bound Multinet Emulator.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """Fail parsing multinet handler output.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Error occurred while parsing multinet '
                            'handler output. {0}'.
                            format(additional_error_info), err_code)


class MultinetDeployError(SBEmuError):
    """Contains the exception handling concerning the South-Bound Multinet
    Emulator deploy.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """Fail to deploy multinet workers.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Fail to deploy multinet workers. {0}'.
                            format(additional_error_info), err_code)


class MultinetInitToposError(SBEmuError):
    """Contains the exception handling concerning the initialization of a
    South-Bound Multinet topology
    """
    def __init__(self, additional_error_info='', err_code=1):
        """Fail to initialize multinet topology.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Fail to initialize multinet topology. {0}'.
                            format(additional_error_info), err_code)


class MultinetStartToposError(SBEmuError):
    """Contains the exception handling concerning the staring of a
    South-Bound Multinet topology
    """
    def __init__(self, additional_error_info='', err_code=1):
        """Fail to start multinet topology.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Fail to start multinet topology. {0}'.
                            format(additional_error_info), err_code)


class MultinetGetSwitchesError(SBEmuError):
    """Contains the exception handling concerning the returned switches from
    a the South-Bound Emulator topology
    """
    def __init__(self, additional_error_info='', err_code=1):
        """Fail to get number of switches of multinet topology.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Fail to get multinet topology total switch'
                            ' number. {0}'.format(additional_error_info),
                            err_code)


class MultinetGetFlowsError(SBEmuError):
    """Contains the exception handling concerning the returned flows from
    a the South-Bound Emulator topology
    """
    def __init__(self, additional_error_info='', err_code=1):
        """Fail to get total number of flows of multinet topology.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Fail to get multinet topology total flows'
                            ' number. {0}'.format(additional_error_info),
                            err_code)


class MultinetTraffigGenError(SBEmuError):
    """Contains the exception handling concerning the South-Bound Multinet
    Emulator traffic generator functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """Error while generating traffic in multinet topology.
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Fail generating multinet topology PacketIn'
                            ' and FlowMod traffic. {0}'.
                            format(additional_error_info), err_code)


class MultinetStopToposError(SBEmuError):
    """Contains the exception handling concerning the stopping of a
    South-Bound Multinet topology
    """
    def __init__(self, additional_error_info='', err_code=1):
        """Fail to stop multinet topology
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Fail to stop multinet topology. {0}'.
                            format(additional_error_info), err_code)


class MultinetCleanupError(SBEmuError):
    """Contains the exception handling concerning the South-Bound Multinet
    Emulator cleaning functionality.
    """
    def __init__(self, additional_error_info='', err_code=1):
        """Fail to cleanup multinet workers
        :param additional_error_info: the general error message.
        :param err_code: the specific error code.
        :type str
        :type int
        """
        SBEmuError.__init__(self, 'Fail to cleanup multinet workers. {0}'.
                            format(additional_error_info), err_code)
