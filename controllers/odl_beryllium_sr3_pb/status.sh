#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

# Queries controller status

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd $SCRIPT_DIR

KARAF_PATH="distribution-karaf-0.4.3-Beryllium-SR3"

if [ -d $KARAF_PATH"/bin" ]; then
    cd $KARAF_PATH"/bin"
else
    echo "[status.sh]: The specified KARAF_PATH does not exist. Exiting..."
    exit 1
fi

# Do not remove 2>/dev/null, or else the output result might be corrupted
CONTROLLER_PID=$(./client -u karaf "instance:list" 2>/dev/null | grep "Started" | awk '{print $9}')
if [ -z "$CONTROLLER_PID" ]; then
    echo "0" #controller is  not running
else
    echo "1" #controller is running
fi
