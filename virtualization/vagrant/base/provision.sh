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
    git

