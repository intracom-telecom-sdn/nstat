#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html


SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo $SCRIPT_DIR

MULTINET_LOCATION="https://github.com/intracom-telecom-sdn/multinet.git"

if [ ! -d $SCRIPT_DIR"/multinet" ]; then
    git clone $MULTINET_LOCATION $SCRIPT_DIR"/multinet"
    if [ $? -ne 0 ]; then
        echo "[build.sh] Cloning multinet failed. Exiting ..."
        exit 1
    fi
    rm -rf $SCRIPT_DIR"/multinet/.git"
    mv $SCRIPT_DIR/multinet/* $SCRIPT_DIR
    if [ $? -ne 0 ]; then
        echo "[build.sh] Moving multinet files failed. Exiting ..."
        exit 1
    fi
    rm -rf $SCRIPT_DIR/multinet
fi

echo "[build.sh] Building multinet completed successfully"