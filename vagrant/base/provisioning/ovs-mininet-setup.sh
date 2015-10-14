#!/usr/bin/env bash

git clone http://github.com/mininet/mininet
cd mininet
git checkout -b 2.2.1 2.2.1
./util/install.sh -vnf3
dpkg-reconfigure openvswitch-datapath-dkms
service openflow-switch restart
mn --test pingall