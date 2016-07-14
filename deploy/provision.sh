#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

TEST_USER="jenkins"
#PROXY="http://172.28.40.9:3128"
VENV_DIR="venv"

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

# This user is required to run jenkins jobs and must be the same with the ssh
# user defined in json files of tests
#------------------------------------------------------------------------------
useradd -m -s /bin/bash -p $(openssl passwd -crypt $TEST_USER) -U $TEST_USER
echo "$TEST_USER ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers

TEST_USER_HOME=$(eval echo "~$TEST_USER")

chmod 777 -R /opt

# CONTROLLER_node provisioning actions
#------------------------------------------------------------------------------
apt-get update && apt-get install -y \
    openjdk-7-jdk \
    openjdk-7-jre

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
    pkg-config

# Python installation and other necessary libraries for pip
#------------------------------------------------------------------------------
apt-get update && apt-get install -y \
    python \
    python3.4 \
    python-setuptools \
    python3-setuptools \
    python-dev \
    python3.4-dev \
    python-pypcap \
    libpng-dev \
    freetype6-dev \
    libxml2-dev \
    libxslt1-dev

easy_install3 pip
easy_install pip


# Configure pip options
#------------------------------------------------------------------------------
pip_options="--ignore-installed"
if [ ! -z "$PROXY" ]; then
    pip_options=" --proxy==$PROXY $pip_options"
fi

# Install virtualenv
#------------------------------------------------------------------------------
cd $TEST_USER_HOME
mkdir $VENV_DIR
pip $pip_options install virtualenv
virtualenv --system-site-packages $VENV_DIR


# NSTAT_NODE, oftraf monitoring tool and MULTINET_NODE provisioning actions
#------------------------------------------------------------------------------
# Activate virtualenv
source $VENV_DIR/bin/activate
pip $pip_options install bottle==0.12.8
pip3 $pip_options install bottle==0.12.8
pip3 $pip_options install requests==2.7.0

pip3 $pip_options install pyparsing==2.1.5 \
    tornado==4.3 \
    pytz==2016.4 \
    six==1.10.0 \
    numpy==1.11.1 \
    matplotlib==1.4.3

pip $pip_options install lxml==3.4.4
pip3 $pip_options install lxml==3.4.4
pip $pip_options install cryptography==1.2.1
pip3 $pip_options install cryptography==1.2.1
pip $pip_options install paramiko==1.15.2
pip3 $pip_options install paramiko==1.15.2
pip $pip_options install stdeb==0.8.5
pip $pip_options install dpkt==1.8.6.2
pip3 $pip_options install dpkt==1.8.6.2
pip3 $pip_options install collections-extended=0.7.0
pip3 $pip_options install coveralls==1.1
# Deactivate virtualenv
deactivate


# MININET and OpenVSwitch 2.3.0 installation
#------------------------------------------------------------------------------
apt-get update && apt-get install -y uuid-runtime
cd $TEST_USER_HOME
git clone https://github.com/mininet/mininet.git mininet
cd mininet
git checkout -b 2.2.1 2.2.1
chown -R $TEST_USER:$TEST_USER $TEST_USER_HOME/mininet
./util/install.sh -n3f
./util/install.sh -V 2.3.0
cd $TEST_USER_HOME

# NSTAT installation in TEST_USER home dir
#------------------------------------------------------------------------------
cd $TEST_USER_HOME
git clone https://github.com/intracom-telecom-sdn/nstat.git nstat
cd nstat
git checkout master # checkout to master branch
chown -R $TEST_USER:$TEST_USER $TEST_USER_HOME/nstat
cd $TEST_USER_HOME
