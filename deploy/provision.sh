#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

INSTALL_DIR=$HOME
TEST_USER="jenkins"

# This user is required to run jenkins jobs and must be the same with the ssh
# user defined in json files of tests
#------------------------------------------------------------------------------
useradd -m -s /bin/bash -p $(openssl passwd -crypt $TEST_USER) -U $TEST_USER
echo "$TEST_USER ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers

TEST_USER_HOME=$(eval echo "~$TEST_USER")

chmod 777 -R /opt

# Generic provisioning actions
#------------------------------------------------------------------------------
apt-get update && apt-get install -y \
    git \
    unzip \
    wget \
    mz \
    wireshark \
    openssh-client \
    openssh-server \
    bzip2 \
    openssl \
    net-tools

# CONTROLLER_node provisioning actions
#------------------------------------------------------------------------------
apt-get install -y \
    openjdk-7-jdk \
    openjdk-7-jre

# MT-Cbench_node provisioning actions
#------------------------------------------------------------------------------
apt-get install -y \
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

# NSTAT_NODE, oftraf monitoring tool and MULTINET_NODE provisioning actions
#------------------------------------------------------------------------------
apt-get install -y \
    python \
    python3.4 \
    python-setuptools \   # (20.7.0)
    python3-setuptools \  # (20.7.0)
    python-dev \
    python3.4-dev \
    python-pip \          # (8.0.2)
    python3-pip \         # (8.0.2)
    python3-bottle \     # (0.12.8)
    python3-requests \   # (2.7.0)
    python3-matplotlib \ # (1.4.3)
    python3-lxml \       # (3.4.4)
    python-lxml \        # (3.4.4)
    python-paramiko \    # (1.15.2)
    python-pypcap \
    python-dpkt \        # (1.8.6.2)
    python-bottle        # (0.12.8)

# PYTHON3.4 NSTAT necessary libraries
#------------------------------------------------------------------------------
easy_install3 pip        # (8.0.2)
pip3 install paramiko    # (1.15.2)
pip3 install collections-extended

# MININET and OpenVSwitch 2.3.0 installation
#------------------------------------------------------------------------------
apt-get install -y uuid-runtime
git clone https://github.com/mininet/mininet.git $INSTALL_DIR/mininet
cd $INSTALL_DIR/mininet
git checkout -b 2.2.1 2.2.1
./util/install.sh -n3f
./util/install.sh -V 2.3.0
cd $INSTALL_DIR

# NSTAT installation in TEST_USER home dir
#------------------------------------------------------------------------------
git clone https://github.com/intracom-telecom-sdn/nstat.git $TEST_USER_HOME/nstat
cd $TEST_USER_HOME/nstat
git checkout master # checkout to master branch
chown -R $TEST_USER:$TEST_USER $TEST_USER_HOME/nstat
cd $INSTALL_DIR
