#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
# ------------------------------------------------------------------------------
# Display distribution release version
#-------------------------------------------------------------------------------

INSTALL_DIR=$HOME

# Generic provisioning actions
#-------------------------------------------------------------------------------
apt-get update && apt-get install -y \
    git \
    unzip \
    wget \
    mz \
    wireshark \
    openssh-client \
    openssh-server \
    net-tools

# CONTROLLER_node provisioning actions
#-------------------------------------------------------------------------------
apt-get install -y \
    openjdk-7-jdk \
    openjdk-7-jre

# MT-Cbench_node provisioning actions
#-------------------------------------------------------------------------------
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
    bzip2 \
    openssl

# PYTHON installation
#-------------------------------------------------------------------------------
apt-get install -y \
    python-dev \
    python-setuptools \
    python3.4-dev \
    python3-setuptools \
    python \
    python3.4 \
    python-pip \
    python3-pip

# PYTHON extra libraries
#-------------------------------------------------------------------------------
apt-get install -y \
    python3-bottle \
    python3-requests \
    python3-matplotlib \
    python3-lxml \
    python-lxml \
    python-paramiko \
    python-pypcap \
    python-dpkt \
    python-bottle

# PYTHON3.4 NSTAT necessary libraries
#-------------------------------------------------------------------------------
easy_install3 pip
pip3 install paramiko
pip3 install collections-extended


# MININET and OpenVSwitch 2.3.0 installation
#-------------------------------------------------------------------------------
apt-get install -y uuid-runtime
git clone https://github.com/mininet/mininet.git $INSTALL_DIR/mininet
cd $INSTALL_DIR/mininet
git checkout -b 2.2.1 2.2.1
./util/install.sh -n3f
./util/install.sh -V 2.3.0
cd $INSTALL_DIR

# NSTAT installation
#-------------------------------------------------------------------------------
git clone https://github.com/intracom-telecom-sdn/nstat.git $INSTALL_DIR/nstat
cd $INSTALL_DIR/nstat
git checkout master # checkout to master branch
cd $INSTALL_DIR