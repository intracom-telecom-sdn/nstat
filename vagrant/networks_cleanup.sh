#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html


SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo $SCRIPT_DIR

declare -a vmslist=("vm_mt_cbench" "vm_controller" "vm_mininet" "vm_nb_generator" "vm_nstat")

for i in "${vmslist[@]}"; do
	echo $i
	vboxmanage controlvm $i poweroff
	vboxmanage unregistervm $i --delete
done


for item in $( ls -1d $SCRIPT_DIR/*/ ); do
	echo $item
	cd $item
	vagrant destroy -f
	virsh shutdown $item"_nstat_vm_packaged"
    virsh destroy $item"_nstat_vm_packaged"
    virsh undefine $item"_nstat_vm_packaged"
    rm -rf .vagrant
	cd $SCRIPT_DIR
done

for network in $(vboxmanage list hostonlyifs | egrep  '^Name:.*' | awk '{print $2}');
do
    vboxmanage hostonlyif remove $network
done

virsh net-destroy --network vagrant-libvirt-nstat
virsh net-undefine --network vagrant-libvirt-nstat


echo "[networks_cleanup.sh] Cleanup of multinet completed successfully"