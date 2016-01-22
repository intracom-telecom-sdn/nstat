#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

#Input parameters
#    1. IP address of the machine where oftraf is running
#    2. REST port where oftraf REST server listens for requests
#    3. Openflow protocol port number

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo $SCRIPT_DIR


sudo python $SCRIPT_DIR/oftraf.py --rest-host $1 --rest-port $2 --of-port $3 --ifname $(ip addr show | grep $1 | awk '{print $5}') --server
if [ $? -ne 0 ]; then
    echo "[start.sh] start of oftraf failed. Exiting ..."
    exit 1
fi