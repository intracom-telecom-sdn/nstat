#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

TEST_USER="jenkins"
BASE_DIR=/opt
VENV_DIR="venv"

# Add here the proxy settings (http://<proxy>:<port>) or else leave it empty
PROXY="http://172.28.40.9:3128"

# Generic provisioning actions
#------------------------------------------------------------------------------
apt-get update && apt-get install -y \
    git \
    unzip \
    wget \
    openssh-client \
    openssh-server \
    bzip2 \
    openssl \
    net-tools

# This user is required to run jenkins jobs and must be the same with the ssh
# user defined in json files of tests
#------------------------------------------------------------------------------
useradd -m -s /bin/bash -p $(openssl passwd -crypt $TEST_USER) -U $TEST_USER
echo "$TEST_USER ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers
chmod 777 -R $BASE_DIR

# CONTROLLER_node provisioning actions
#------------------------------------------------------------------------------
apt-get update && apt-get install -y \
    openjdk-7-jdk

# MT-Cbench_node provisioning actions
#------------------------------------------------------------------------------
apt-get update && apt-get install -y \
    build-essential \
    snmp \
    libsnmp-dev \
    snmpd \
    libpcap-dev \
    autoconf \
    make \
    automake \
    libtool \
    libconfig-dev \
    libssl-dev \
    pkg-config \
    libfreetype6-dev


sudo apt-get install python3-pip
sudo apt-get install python-virtualenv
pip3 install --upgrade pip



# Python installation and other necessary libraries for pip
#------------------------------------------------------------------------------
#apt-get update && apt-get install -y \
    #    python \
    #python3.4 \
    #python-setuptools \
    #python3-setuptools \
    #python-dev \
    #python3.4-dev \
    #python-pypcap \
    #libpng-dev \
    #libfreetype6-dev \
    #libxml2-dev \
    #libxslt1-dev \
    #python-virtualenv
#easy_install3 pip
#easy_install pip
#easy_install setuptools


# Configure pip options
#------------------------------------------------------------------------------
pip_options=""
# pip_options="--ignore-installed"
if [ ! -z "$PROXY" ]; then
    pip_options=" --proxy==$PROXY $pip_options"
fi

# Install virtualenv
#------------------------------------------------------------------------------
mkdir $BASE_DIR/$VENV_DIR
virtualenv --system-site-packages $BASE_DIR/$VENV_DIR
virtualenv $BASE_DIR/$VENV_DIR

# NSTAT_node, oftraf monitoring tool and Multinet_node provisioning actions
#------------------------------------------------------------------------------
# Activate virtualenv
source $BASE_DIR/$VENV_DIR/bin/activate
pip install -r requirements_p2.txt
pip3 install -r requirements_p3.txt
# Deactivate virtualenv
deactivate

# Multinet_node
#------------------------------------------------------------------------------
apt-get update && apt-get install -y \
    uuid-runtime \
    mz
git clone https://github.com/mininet/mininet.git $BASE_DIR/mininet
git --git-dir=$BASE_DIR/mininet/.git --work-tree=$BASE_DIR/mininet branch -a
git --git-dir=$BASE_DIR/mininet/.git --work-tree=$BASE_DIR/mininet checkout -b 2.2.1 2.2.1
#cd $BASE_DIR/mininet
#git checkout -b 2.2.1 2.2.1
chown -R $TEST_USER:$TEST_USER $BASE_DIR/mininet
./mininet/util/install.sh -n3f
./mininet/util/install.sh -V 2.3.0

# NSTAT installation in TEST_USER home dir
#------------------------------------------------------------------------------
git clone https://github.com/intracom-telecom-sdn/nstat.git $BASE_DIR/nstat
git --git-dir=$BASE_DIR/nstat/.git --work-tree=$BASE_DIR/nstat branch -a
git --git-dir=$BASE_DIR/nstat/.git --work-tree=$BASE_DIR/nstat checkout master
#cd $BASE_DIR/nstat
#git checkout master # checkout to master branch

chown -R $TEST_USER:$TEST_USER $BASE_DIR/nstat
