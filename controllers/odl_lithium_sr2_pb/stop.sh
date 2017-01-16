#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

# Stops controller

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd $SCRIPT_DIR

KARAF_PATH="distribution-karaf-0.3.2-Lithium-SR2"

if [ -d $KARAF_PATH"/bin" ]; then
    cd $KARAF_PATH"/bin"
else
    echo "[stop.sh]: The specified KARAF_PATH does not exist. Exiting..."
    exit 1
fi

CONTROLLER_PID=$(./client -u karaf "instance:list" 2>/dev/null | grep "Started" | awk '{print $9}')

if [ ! -z "$CONTROLLER_PID" ]; then
    echo "Found Karaf process id:" $CONTROLLER_PID
    echo "Killing it..."

    kill -9 $CONTROLLER_PID
    if [ $? -eq 0 ]; then
      echo "Karaf process " $CONTROLLER_PID " stopped successfully!"
    else
      echo "Karaf process " $CONTROLLER_PID " did not stop successfully!"
      exit 1
    fi
else
    echo "No Karaf process id found"
    exit 1
fi
