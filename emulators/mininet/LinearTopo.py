# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Customly-booted Mininet topology (linear type)"""

from CustomBootedTopo import CustomBootedTopo
import logging
from mininet import link

class LinearTopo(CustomBootedTopo):
    """Linear-type topology"""

    def _add_links_to_switch(self, switch, startflag):
        """
        Adds links between a newly added switch and the last switch in the 
        linear topology.

        :param switch: the newly added switch
        :param startflag: controls whether the newly added switch will become
                          active in the existing topology
        :type switch: mininet.node.OVSSwitch 
        :type startflag: bool
        """

        # Create links between switch(j) and switch(j-1): linear connection
        last_sw = self._switches[-1]
        lnk = link.Link(last_sw, switch)
        logging.debug('[mininet] Linking switch {0} with {1}'.
                      format(last_sw.name, switch.name))

        if last_sw not in self._switch_links.keys():
            self._switch_links[last_sw] = []
        if switch not in self._switch_links.keys():
            self._switch_links[switch] = []

        self._switch_links[last_sw].append(lnk)
        self._switch_links[switch].append(lnk)

        if startflag:
            last_sw.start([self._controller])
