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

if [ ! -d $SCRIPT_DIR"/controllers/odl_boron_pb" ]; then
    git clone -b get-handlers $NSTAT_SDN_CONTROLLER_LOCATION $SCRIPT_DIR"/controllers/odl_boron_pb"
    if [ $? -ne 0 ]; then
    	echo "Kostas"
        echo "[build.sh] Cloning nstat-sdn-controllers failed. Exiting ..."
        exit 1
    fi
    rm -rf $SCRIPT_DIR"/controllers/odl_boron_pb/.git"
    mv $SCRIPT_DIR/controllers/odl_boron_pb/controllers/odl_boron_pb/* $SCRIPT_DIR/controllers/odl_boron_pb
    if [ $? -ne 0 ]; then
        echo "[build.sh] Moving nstat-sdn-controllers files failed. Exiting ..."
        exit 1
    fi
    rm -rf $SCRIPT_DIR"/controllers/odl_boron_pb/controllers/odl_boron_pb"
fi

echo "[build.sh] Building nstat-sdn-controllers completed successfully"