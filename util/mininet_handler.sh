#! /bin/bash
sudo mn --topo single,3 --switch ovsk,protocols=OpenFlow13 --controller=remote,ip=<IP_address>,port=6653
