#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
# ------------------------------------------------------------------------------
# Display distribution release version
#-------------------------------------------------------------------------------

# Remove comments from the following lines to make proxy settings persistent
# ------------------------------------------------------------------------------
export http_proxy='172.28.40.9:3128'
export https_proxy='172.28.40.9:3128'

sudo echo "http_proxy="$http_proxy >> /etc/environment
sudo echo "https_proxy="$https_proxy >> /etc/environment
sudo echo "HTTP_PROXY="$http_proxy >> /etc/environment
sudo echo "HTTPS_PROXY="$https_proxy >> /etc/environment
# ------------------------------------------------------------------------------

# Install NSTAT for jenkins user
#-------------------------------------------------------------------------------
sudo git clone https://github.com/intracom-telecom-sdn/nstat.git /home/jenkins/nstat
sudo chmod -R 777 /home/jenkins/nstat
sudo chown -R jenkins:jenkins /home/jenkins/nstat

cd /home/jenkins/nstat
git branch -a       # list NSTAT branches
git checkout master # checkout to master branch
#git tag -l          # list NSTAT tags
cd $HOME

# Install NSTAT for vagrant user
#-------------------------------------------------------------------------------
sudo git clone https://github.com/intracom-telecom-sdn/nstat.git /home/vagrant/nstat
sudo chmod -R 777 /home/vagrant/nstat
sudo chown -R vagrant:vagrant /home/vagrant/nstat

cd /home/vagrant/nstat
git branch -a       # list NSTAT branches
git checkout master # checkout to master branch
#git tag -l          # list NSTAT tags
#git checkout v1.2   # comment out to check out at a certain tag
cd $HOME

# Giving write access to ./opt (default directory where controller build
# handler downloads OpenDaylight from official repository)
#-------------------------------------------------------------------------------
cd /
sudo chmod 777 -R /opt
cd $HOME
