#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
# -----------------------------------------------------------------------------
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

BASE_DIR="/opt"
VENV_DIR_NSTAT="venv_nstat"
VENV_DIR_MULTINET="venv_multinet"

# PROXY value is passed either from Vagrantfile/Dockerfile
#------------------------------------------------------------------------------
PROXY=$1

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
chmod 777 -R $BASE_DIR

# Controller node provisioning actions
#------------------------------------------------------------------------------
apt-get update && apt-get install -y \
    openjdk-7-jdk

# MT-Cbench node provisioning actions
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
    libffi-dev \
    libssl-doc \
    pkg-config

# Python installation and other necessary libraries for pip
#------------------------------------------------------------------------------
apt-get update && apt-get install -y \
    python \
    python3.4 \
    python-dev \
    python3.4-dev \
    python3-matplotlib \
    python3-lxml \
    python-pypcap \
    python-pip \
    python3-pip \
    python-virtualenv

# Configure pip options
#------------------------------------------------------------------------------
pip_options=""

if [ ! -z "$PROXY" ]; then
    pip_options=" --proxy==$PROXY $pip_options"
fi

pip3 $pip_options install --upgrade pip

# NSTAT node provisioning actions
#------------------------------------------------------------------------------
mkdir $BASE_DIR/$VENV_DIR_NSTAT
virtualenv --system-site-packages $BASE_DIR/$VENV_DIR_NSTAT

wget https://raw.githubusercontent.com/intracom-telecom-sdn/nstat/develop_provision_review/deploy/requirements.txt -P $BASE_DIR
source $BASE_DIR/$VENV_DIR_NSTAT/bin/activate
pip3 $pip_options install -r $BASE_DIR/requirements.txt
rm -rf $BASE_DIR/requirements.txt
deactivate

apt-get update && apt-get install -y \
    uuid-runtime \
    mz
git clone https://github.com/mininet/mininet.git $BASE_DIR/mininet
git --git-dir=$BASE_DIR/mininet/.git --work-tree=$BASE_DIR/mininet checkout -b 2.2.1 2.2.1

/$BASE_DIR/mininet/util/install.sh -n3f
/$BASE_DIR/mininet/util/install.sh -V 2.3.0

# Multinet node
#------------------------------------------------------------------------------
mkdir $BASE_DIR/$VENV_DIR_MULTINET
virtualenv --system-site-packages $BASE_DIR/$VENV_DIR_MULTINET

git clone -b master https://github.com/intracom-telecom-sdn/multinet.git $BASE_DIR"/multinet"
source $BASE_DIR/$VENV_DIR_MULTINET/bin/activate
pip $pip_options install -r $BASE_DIR"/multinet/requirements.txt"
deactivate

# NSTAT installation
#------------------------------------------------------------------------------
git clone https://github.com/intracom-telecom-sdn/nstat.git $BASE_DIR/nstat
git --git-dir=$BASE_DIR/nstat/.git --work-tree=$BASE_DIR/nstat checkout v1.3
apt-get clean