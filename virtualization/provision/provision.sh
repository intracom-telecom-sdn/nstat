#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
# ------------------------------------------------------------------------------
# Display distribution release version
#-------------------------------------------------------------------------------

BASE_DIR=$(pwd)
cd $BASE_DIR

# Remove comments from the following lines to make proxy settings persistent
# ------------------------------------------------------------------------------
#http_proxy="http://172.28.40.9:3128/"
#https_proxy="http://172.28.40.9:3128/"
#ftp_proxy="http://172.28.40.9:3128/"
#export http_proxy
#export https_proxy
#export ftp_proxy
#printf -v no_proxy '%s,' 192.168.121.{1..255};export no_proxy="${no_proxy%,}"",127.0.0.1,localhost";

#echo "http_proxy="$http_proxy | sudo tee -a /etc/environment
#echo "https_proxy="$https_proxy | sudo tee -a /etc/environment
#echo "ftp_proxy="$ftp_proxy | sudo tee -a /etc/environment
#echo "no_proxy="$no_proxy | sudo tee -a /etc/environment
#echo "HTTP_PROXY="$http_proxy | sudo tee -a /etc/environment
#echo "HTTPS_PROXY="$https_proxy | sudo tee -a /etc/environment
#echo "FTP_PROXY="$ftp_proxy | sudo tee -a /etc/environment
#echo "NO_PROXY="$no_proxy | sudo tee -a /etc/environment
#if [ ! -f /etc/apt/apt.conf ]; then
#    sudo touch /etc/apt/apt.conf
#fi
#echo 'Acquire::http::Proxy "http://'$http_proxy'/";' | sudo tee -a /etc/apt/apt.conf
#echo 'Acquire::ftp::Proxy "ftp://'$ftp_proxy'/";' | sudo tee -a /etc/apt/apt.conf
#echo 'Acquire::https::Proxy "https://'$https_proxy'/";' | sudo tee -a /etc/apt/apt.conf

# ------------------------------------------------------------------------------

# Create a jenkins user with jenkins password and passwordless sudo privileges
# ------------------------------------------------------------------------------
#sudo useradd -m -s /bin/bash -p $(openssl passwd -crypt jenkins) -U jenkins
#echo "jenkins ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers

# Prevent headers and kernels updates. Mininet will not work with Linux kernel newer than 3.12.x
apt-mark hold linux-image-generic linux-headers-generic

# NSTAT node necessary tools
#-------------------------------------------------------------------------------
apt-get update && sudo apt-get install --force-yes -y \
    git \
    unzip \
    wget \
    iperf \
    mz \
    wireshark \
    net-tools

# CONTROLLER_node necessary tools
#-------------------------------------------------------------------------------
apt-get install --force-yes -y \
    openssh-client \
    openssh-server \
    openjdk-7-jdk \
    openjdk-7-jre


# SOUTHBOUND_GEN_node necessary tools (build tools)
#-------------------------------------------------------------------------------
apt-get install --force-yes -y \
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
    fakeroot \
    debhelper \
    libssl-dev \
    pkg-config \
    bzip2 \
    openssl \
    procps

# Python installation
#-------------------------------------------------------------------------------
apt-get install --force-yes -y \
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
apt-get install --force-yes -y \
    python3-bottle \
    python3-requests \
    python3-matplotlib \
    python3-lxml \
    python-lxml \
    python-paramiko \
    python-pypcap \
    python-dpkt \
    python-bottle

# Upgrade Python setuptools/pip
#-------------------------------------------------------------------------------
pip install --upgrade pip
pip3 install --upgrade pip3
pip install --upgrade setuptools
pip3 install --upgrade setuptools

# Install NSTAT necessary python3.4 tools
#-------------------------------------------------------------------------------
easy_install3 pip
pip3 install paramiko
pip3 install collections-extended

# Giving write access to ./opt (default directory where controller build
# handler downloads OpenDaylight from official repository)
#-------------------------------------------------------------------------------
cd /
sudo chmod 777 -R /opt
cd $BASE_DIR

# MININET installation
#-------------------------------------------------------------------------------
sudo apt-get update && sudo apt-get install --force-yes -y uuid-runtime
git clone https://github.com/mininet/mininet.git /opt/mininet
cd /opt/mininet
git checkout -b 2.2.1 2.2.1
./util/install.sh -vwn3f
cd $BASE_DIR

# Install NTSTAT for vagrant user
#-------------------------------------------------------------------------------
git clone https://github.com/intracom-telecom-sdn/nstat.git /opt/nstat
cd /home/vagrant/nstat
git branch -a # list NSTAT branches
git checkout master # checkout to master branch
git tag -l # list NSTAT tags
cd $BASE_DIR

# Install NSTAT for JENKINS user
#-------------------------------------------------------------------------------
git clone https://github.com/intracom-telecom-sdn/nstat.git /opt/nstat
#sudo chmod -R 777 /home/jenkins/nstat
#sudo chown -R jenkins:jenkins /home/jenkins/nstat

cd /opt/nstat
git branch -a       # list NSTAT branches
git checkout master # checkout to master branch
#git tag -l          # list NSTAT tags
cd $BASE_DIR


