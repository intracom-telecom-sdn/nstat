#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

# If Boron zip exists in /opt, it extracts it in the
# current directory (the "fast" path).
# If it doesn't exist, it downloads it in /opt and them extracts it.

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo $SCRIPT_DIR

NSTAT_SDN_CONTROLLER_LOCATION="https://github.com/intracom-telecom-sdn/nstat-sdn-controllers.git"
NSTAT_SDN_CONTROLLER_HANDLERS="controllers/odl_boron_pb"

if [ ! -d $SCRIPT_DIR/$NSTAT_SDN_CONTROLLER_HANDLERS ]; then
    git clone -b master $NSTAT_SDN_CONTROLLER_LOCATION $SCRIPT_DIR/nstat-sdn-controllers""
    if [ $? -ne 0 ]; then
        echo "[build.sh] Cloning nstat-sdn-controllers failed. Exiting ..."
        exit 1
    fi
    rm -rf $SCRIPT_DIR"/nstat-sdn-controllers/.git"
    mv $SCRIPT_DIR/nstat-sdn-controllers/$NSTAT_SDN_CONTROLLER_HANDLERS/* $SCRIPT_DIR
    if [ $? -ne 0 ]; then
        echo "[build.sh] Moving nstat-sdn-controllers files failed. Exiting ..."
        exit 1
    fi
    rm -rf $SCRIPT_DIR/nstat-sdn-controllers
fi

echo "[build.sh] Building nstat-sdn-controllers completed successfully"