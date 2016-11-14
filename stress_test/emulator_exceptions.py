# Copyright (c) 2016 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Implementation of custom SB emulator exception classes."""


class SBEmuError(Exception):
    """Base-class for all SB emulators exceptions raised by this module."""
    def __init__(self, err_msg=None, err_code=1):
        self.err_code = err_code
        if err_msg is None:
            Exception.__init__(self, 'SB emulator generic exception')
            self.err_msg = 'SB emulator generic exception'
        else:
            Exception.__init__(self, err_msg)
            self.err_msg = err_msg


class SBEmuNodeConnectionError(SBEmuError):
    """A SB emulator node connection error."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Fail to establish ssh connection with '
                            'SB emulator node. {0}'.
                            format(additional_error_info))


class SBEmuBuildError(SBEmuError):
    """A SB emulator build error."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'SB emulator build failure. {0}'.
                            format(additional_error_info))


class SBEmuCleanupError(SBEmuError):
    """A SB emulator cleanup error."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'SB emulator cleanup failure. {0}'.
                            format(additional_error_info))


class MTCbenchRunError(SBEmuError):
    """MTCbench fail to run error."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Error occurred while running MTCbench. {0}'.
                            format(additional_error_info))


class MultinetConfGenerateError(SBEmuError):
    """Fail generate configuration file for multinet."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Error occurred while generating multinet '
                            'configuration file. {0}'.
                            format(additional_error_info))


class MultinetOutputParsingError(SBEmuError):
    """Fail parsing multinet handler output."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Error occurred while parsing multinet '
                            'handler output. {0}'.
                            format(additional_error_info))


class MultinetDeployError(SBEmuError):
    """Fail to deploy multinet workers."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Fail to deploy multinet workers. {0}'.
                            format(additional_error_info))


class MultinetInitToposError(SBEmuError):
    """Fail to initialize multinet topology."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Fail to initialize multinet topology. {0}'.
                            format(additional_error_info))


class MultinetStartToposError(SBEmuError):
    """Fail to start multinet topology."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Fail to start multinet topology. {0}'.
                            format(additional_error_info))


class MultinetGetSwitchesError(SBEmuError):
    """Fail to get number of switches of multinet topology."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Fail to get multinet topology total switch'
                            ' number. {0}'.format(additional_error_info))


class MultinetGetFlowsError(SBEmuError):
    """Fail to get total number of flows of multinet topology."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Fail to get multinet topology total flows'
                            ' number. {0}'.format(additional_error_info))


class MultinetTraffigGenError(SBEmuError):
    """Error while generating traffic in multinet topology."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Fail generating multinet topology PacketIn'
                            ' and FlowMod traffic. {0}'.
                            format(additional_error_info))


class MultinetStopToposError(SBEmuError):
    """Fail to stop multinet topology."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Fail to stop multinet topology. {0}'.
                            format(additional_error_info))


class MultinetCleanupError(SBEmuError):
    """Fail to cleanup multinet workers."""
    def __init__(self, additional_error_info=''):
        SBEmuError.__init__(self, 'Fail to cleanup multinet workers. {0}'.
                            format(additional_error_info))