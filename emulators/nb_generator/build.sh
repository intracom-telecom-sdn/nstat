#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html


SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo $SCRIPT_DIR

NSTAT_NB_GENERATOR_LOCATION="https://github.com/intracom-telecom-sdn/nstat-nb-generator.git"

if [ ! -d $SCRIPT_DIR"/nstat-nb-generator" ]; then
    git clone -b nb-gen-fix $NSTAT_NB_GENERATOR_LOCATION $SCRIPT_DIR"/nstat-nb-generator"
    if [ $? -ne 0 ]; then
        echo "[build.sh] Cloning nstat-nb-generator failed. Exiting ..."
        exit 1
    fi
    rm -rf $SCRIPT_DIR"/nstat-nb-generator/.git"
    mv $SCRIPT_DIR/nstat-nb-generator/* $SCRIPT_DIR
    if [ $? -ne 0 ]; then
        echo "[build.sh] Moving nstat-nb-generator files failed. Exiting ..."
        exit 1
    fi
    rm -rf $SCRIPT_DIR/nstat-nb-generator
fi

echo "[build.sh] Building nstat-nb-generator completed successfully"