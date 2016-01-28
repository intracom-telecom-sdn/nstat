#!/bin/bash

vboxmanage hostonlyif remove <host_only_network_name>
virsh net-destroy --network <host_only_network_name>