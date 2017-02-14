#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html


SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo $SCRIPT_DIR

NSTAT_NB_EMULATOR_LOCATION="https://github.com/intracom-telecom-sdn/nstat-nb-emulator.git"

if [ ! -d $SCRIPT_DIR"/nstat-nb-emulator" ]; then
    git clone -b v.1.0 $NSTAT_NB_EMULATOR_LOCATION $SCRIPT_DIR"/nstat-nb-emulator"
    if [ $? -ne 0 ]; then
        echo "[build.sh] Cloning nstat-nb-emulator failed. Exiting ..."
        exit 1
    fi
    rm -rf $SCRIPT_DIR"/nstat-nb-emulator/.git"
    mv $SCRIPT_DIR/nstat-nb-emulator/* $SCRIPT_DIR
    if [ $? -ne 0 ]; then
        echo "[build.sh] Moving nstat-nb-emulator files failed. Exiting ..."
        exit 1
    fi
    rm -rf $SCRIPT_DIR/nstat-nb-emulator
fi

echo "[build.sh] Building nstat-nb-emulator completed successfully"