#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html


SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo $SCRIPT_DIR

OFTRAF_LOCATION="https://github.com/intracom-telecom-sdn/oftraf.git"

if [ ! -d $SCRIPT_DIR"/oftraf" ]; then
    git clone $OFTRAF_LOCATION $SCRIPT_DIR"/oftraf"
    if [ $? -ne 0 ]; then
        echo "[build.sh] Cloning oftraf failed. Exiting ..."
        exit $?
    fi
    rm -rf $SCRIPT_DIR"/oftraf/.git"
    mv $SCRIPT_DIR/oftraf/* $SCRIPT_DIR
    if [ $? -ne 0 ]; then
        echo "[build.sh] Moving oftraf files failed. Exiting ..."
        exit $?
    fi
    rm -rf $SCRIPT_DIR/oftraf
fi

echo "[build.sh] Building oftraf completed successfully"