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
MAX_START_TRIES=10
IFNAME=$(sudo ip addr show | grep $1"/" | awk '{print $NF}')

#nohup sudo python $SCRIPT_DIR/oftraf.py --rest-host $1 --rest-port $2 --of-port $3 --ifname $IFNAME --server &
sudo bash $SCRIPT_DIR/venv_handler.sh $4 $SCRIPT_DIR/oftraf.py $1 $2 $3 $IFNAME

if [ $? -ne 0 ]; then
    echo "[start.sh] start of oftraf failed. Exiting ..."
    exit $?
fi

tries=1
until [ $(sudo netstat -atupn --numeric-ports  2>&1 | grep "LISTEN" | grep "$1:$2 "| wc -l) -ge 1 ];
do
    sleep 2
    tries=$(( $tries + 1 ))
    if [ "$tries" -ge "$MAX_START_TRIES" ];
    then
        echo "[start.sh] Failed to start oftraf. Exiting ..."
        exit 1
    fi
done