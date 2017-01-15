#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

#Input parameters
#    1. IP address of oftraf REST server
#    2. REST port where oftraf REST server listens for requests

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo $SCRIPT_DIR

for i in $(sudo netstat -atupn --numeric-ports  2>&1 | grep "LISTEN" | grep "$1:$2 ");
do
    if [ $(echo $i | grep '/') ];
    then
        sudo kill -9 $(echo $i |awk -F'/' '{print $1}')
        if [ $? -ne 0 ]; then
            echo "[stop.sh] stop of oftraf failed. Exiting ..."
            exit $?
        fi
    fi
done

