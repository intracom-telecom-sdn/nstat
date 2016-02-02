#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
# ------------------------------------------------------------------------------
# Display distribution release version
#-------------------------------------------------------------------------------

# Install NSTAT necessary tools
#-------------------------------------------------------------------------------
sudo apt-get update && sudo apt-get install --force-yes -y \
    git \
    unzip \
    wget \
    iperf \
    mz \
    wireshark \
    net-tools

# build tools
#-------------------------------------------------------------------------------
sudo apt-get install --force-yes -y \
    snmp \
    libsnmp-dev \
    snmpd \
    libpcap-dev \
    autoconf \
    make \
    automake \
    libtool \
    libconfig-dev

# ssh service & java installation
#-------------------------------------------------------------------------------
sudo apt-get install --force-yes -y \
    openssh-client \
    openssh-server \
    openjdk-7-jdk \
    openjdk-7-jre

# Python installation
#-------------------------------------------------------------------------------
sudo apt-get install --force-yes -y \
    build-essential \
    python-dev \
    python-setuptools \
    python3.4-dev \
    python3-setuptools \
    python \
    python3.4 \
    python-pip \
    python3-pip

# Install Python libraries
#-------------------------------------------------------------------------------
sudo apt-get install --force-yes -y \
    python3-bottle \
    python3-requests \
    python3-matplotlib \
    python3-lxml \
    python-lxml \
    python-paramiko \
    python-pypcap \
    python-dpkt \
    python-bottle

# Install NSTAT necessary python3.4 tools
#-------------------------------------------------------------------------------
sudo easy_install3 pip
sudo pip3 install paramiko
sudo pip3 install collections-extended

# Install Mininet
#-------------------------------------------------------------------------------
git clone https://github.com/mininet/mininet.git
cd mininet
git checkout -b 2.2.1 2.2.1
./util/install.sh -vwnf3
cd $HOME

# Install NTSTAT
#-------------------------------------------------------------------------------
git clone https://github.com/intracom-telecom-sdn/nstat.git nstat
cd nstat
git branch -a # list NSTAT branches
git checkout master # checkout to master branch
git tag -l # list NSTAT tags
# git checkout v1.2 comment out to check out at a certain tag
cd $HOME

# Giving write access to ./opt (default directory where controller build
# handler downloads OpenDaylight from official repository)
#-------------------------------------------------------------------------------
cd /
sudo chmod 777 -R /opt
cd $HOME
