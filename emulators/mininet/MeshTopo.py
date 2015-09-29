# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Customly-booted Mininet topology (mesh type)"""

from CustomBootedTopo import CustomBootedTopo
import logging
from mininet import link

class MeshTopo(CustomBootedTopo):
    """Mesh-type topology"""

    def _add_links_to_switch(self, switch, startflag):
        """
        Adds links between a newly added switch and all the rest switches in 
        the mesh topology.

        :param switch: the newly added switch
        :param startflag: controls whether the newly added switch will become
                          active in the existing topology
        :type switch: mininet.node.OVSSwitch 
        :type startflag: bool
        """

        if switch not in self._switch_links.keys():
            self._switch_links[switch] = []
        
        # create links between the new switch and every other switch in the
        # topology
        for curr_sw in self._switches:
            lnk = link.Link(curr_sw, switch)
            logging.info('[mininet] Linking switch {0} with {1}'.
                         format(curr_sw.name, switch.name))

            if curr_sw not in self._switch_links.keys():
                self._switch_links[curr_sw] = []

            self._switch_links[curr_sw].append(lnk)
            self._switch_links[switch].append(lnk)

            if startflag:
                curr_sw.start([self._controller])
