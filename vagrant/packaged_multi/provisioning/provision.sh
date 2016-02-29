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
sudo apt-get update

export http_proxy='172.28.40.9:3128'
export https_proxy='172.28.40.9:3128'

# Install NTSTAT
#-------------------------------------------------------------------------------
git clone https://github.com/intracom-telecom-sdn/nstat.git nstat
cd nstat
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
