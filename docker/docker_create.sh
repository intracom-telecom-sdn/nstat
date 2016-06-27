#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

# If Beryllum zip exists in /opt, it extracts it in the
# current directory (the "fast" path).
# If it doesn't exist, it downloads it in /opt and them extracts it.

CONTAINER_IMAGE='nstat'
CONTAINER_NAME='container01'
CONTAINER_SUBNET='192.168.100.0/24'
CONTAINER_HOSTNAME='worker01'
CONTAINER_NETWORK_NAME='docker-nstat'

cd node_nstat

sudo docker network create --subnet=$CONTAINER_SUBNET -o --icc,--ip-masq,--mtu=1500 $CONTAINER_NETWORK_NAME
sudo docker pull ubuntu:14.04
sudo docker run --privileged -h=$CONTAINER_HOSTNAME --name=$CONTAINER_NAME --net=$CONTAINER_NETWORK_NAME ubuntu:14.04 /bin/bash
sudo docker build .
sudo docker ps -a
sudo docker commit $CONTAINER_NAME $CONTAINER_IMAGE

# For creating further containers out of CONTAINER_NAME
# sudo docker run -it --privileged -h=$CONTAINER_HOSTNAME --name=$CONTAINER_NAME --net=$CONTAINER_NETWORK_NAME $CONTAINER_IMAGE /bin/bash