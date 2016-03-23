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

BASE_DIR=$(pwd)

http_proxy='172.28.40.9:3128'
https_proxy='172.28.40.9:3128'
ftp_proxy='172.28.40.9:3128'

export http_proxy
export https_proxy
export ftp_proxy
printf -v no_proxy '%s,' 192.168.100.{1..255};export no_proxy="${no_proxy%,}"",127.0.0.1,localhost";

echo "http_proxy="$http_proxy | sudo tee -a /etc/environment
echo "https_proxy="$https_proxy | sudo tee -a /etc/environment
echo "ftp_proxy="$ftp_proxy | sudo tee -a /etc/environment
echo "HTTP_PROXY="$http_proxy | sudo tee -a /etc/environment
echo "HTTPS_PROXY="$https_proxy | sudo tee -a /etc/environment
echo "FTP_PROXY="$ftp_proxy | sudo tee -a /etc/environment
echo "no_proxy="$no_proxy | sudo tee -a /etc/environment
if [ ! -f /etc/apt/apt.conf ]; then
    sudo touch /etc/apt/apt.conf
fi
echo 'Acquire::http::Proxy "http://'$http_proxy'/";' | sudo tee -a /etc/apt/apt.conf
echo 'Acquire::ftp::Proxy "ftp://'$ftp_proxy'/";' | sudo tee -a /etc/apt/apt.conf
echo 'Acquire::https::Proxy "https://'$https_proxy'/";' | sudo tee -a /etc/apt/apt.conf

sudo apt-get update
sudo apt-get install --force-yes -y mz

# Install NTSTAT
#-------------------------------------------------------------------------------
sudo git clone https://github.com/intracom-telecom-sdn/nstat.git /home/jenkins/nstat
sudo chmod -R 777 /home/jenkins/nstat
sudo chown -R jenkins:jenkins /home/jenkins/nstat

cd /home/jenkins/nstat
git branch -a       # list NSTAT branches
git checkout master # checkout to master branch
#git tag -l          # list NSTAT tags
#git checkout v1.2   # comment out to check out at a certain tag
cd $BASE_DIR

# Giving write access to ./opt (default directory where controller build
# handler downloads OpenDaylight from official repository)
#-------------------------------------------------------------------------------
cd /
sudo chmod 777 -R /opt
cd $BASE_DIR
