# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Customly-booted Mininet topology (disconnected type)"""

from CustomBootedTopo import CustomBootedTopo


class DisconnectedTopo(CustomBootedTopo):
    """ Disconnected-type topology """

    def _add_links_to_switch(self, switch, startflag):
        """
        Adds links between a newly added switch and the rest switches of the
        topology. In the disconnected topology type, no links are added.
        
        :param switch: the newly added switch
        :param startflag: not used since no link with a newly added switch
        takes place
        :type switch: mininet.node.OVSSwitch
        :type startflag: bool
        """

        if len(self._switches) == 1:
            self._switch_links[self._switches[0]] = []

        if switch not in self._switch_links.keys():
            self._switch_links[switch] = []

